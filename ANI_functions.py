#!/usr/bin/python
import subprocess
import argparse
import os
import shutil
from os import listdir
from os.path import isfile, join, isdir

from pyani import anib, anim, tetra, pyani_config, pyani_files
from pyani.run_multiprocessing import multiprocessing_run
from pyani.pyani_config import params_mpl, params_r


def func_ANI_calc(InputFilesDir, comparisonToMake, method, scheduler):

    # Have we got a valid method choice?
    # Dictionary below defines analysis function, and output presentation
    # functions/settings, dependent on selected method.
    methods = {"ANIm": (calculate_anim, pyani_config.ANIM_FILESTEMS),
               "ANIb": (unified_anib, pyani_config.ANIB_FILESTEMS)
              }

    if method not in methods:
        logger.error("ANI method %s not recognised (exiting)" % args.method)
        logger.error("Valid methods are: %s" % methods.keys())
        sys.exit(1)
    logger.info("Using ANI method: %s" % args.method)

    # Have we got a valid scheduler choice?
    schedulers = ["multiprocessing", "SGE"]
    
    if scheduler not in schedulers:
        logger.error("scheduler %s not recognised (exiting)" % args.scheduler)
        logger.error("Valid schedulers are: %s" % '; '.join(schedulers))
        sys.exit(1)
    logger.info("Using scheduler method: %s" % args.scheduler)

    # Get input files
    #logger.info("Identifying FASTA files in %s" % args.indirname)
    infiles = []
    infiles.append(os.path.join(InputFilesDir, comparisonToMake.split('--')[0]))
    infiles.append(os.path.join(InputFilesDir, comparisonToMake.split('--')[1]))

    #infiles = pyani_files.get_fasta_files(comparisonDir)
    logger.info("Input files:\n\t%s" % '\n\t'.join(infiles))

    # Get lengths of input sequences
    #logger.info("Processing input sequence lengths")
    org_lengths = pyani_files.get_sequence_lengths(infiles)
    logger.info("Sequence lengths:\n" +
                os.linesep.join(["\t%s: %d" % (k, v) for
                                 k, v in org_lengths.items()]))

    # Run appropriate method on the contents of the input directory,
    # and write out corresponding results.
    logger.info("Carrying out %s analysis" % args.method)
    results = methods[args.method][0](infiles, org_lengths)

    return results


# Read sequence annotations in from file
def get_labels(filename):
    """Returns a dictionary of alternative sequence labels, or None

    - filename - path to file containing tab-separated table of labels

    Input files should be formatted as <key>\t<label>, one pair per line.
    """
    try:
        labeldict = {}
        with open(filename, 'rU') as fh:
            for line in fh.readlines():
                key, label = line.strip().split('\t')
                labeldict[key] = label
        return labeldict
    except:
        None


# Calculate ANIm for input
def calculate_anim(infiles, org_lengths):
    """Returns ANIm result dataframes for files in input directory.

    - infiles - paths to each input file
    - org_lengths - dictionary of input sequence lengths, keyed by sequence

    Finds ANI by the ANIm method, as described in Richter et al (2009)
    Proc Natl Acad Sci USA 106: 19126-19131 doi:10.1073/pnas.0906412106.

    All FASTA format files (selected by suffix) in the input directory
    are compared against each other, pairwise, using NUCmer (which must
    be in the path). NUCmer output is stored in the output directory.

    The NUCmer .delta file output is parsed to obtain an alignment length
    and similarity error count for every unique region alignment between
    the two organisms, as represented by the sequences in the FASTA files.

    These are processed to give matrices of aligned sequence lengths,
    average nucleotide identity (ANI) percentages, coverage (aligned
    percentage of whole genome), and similarity error cound for each pairwise
    comparison.
    """
    logger.info("Running ANIm")
    logger.info("Generating NUCmer command-lines")
    # Schedule NUCmer runs
    if not args.skip_nucmer:
        cmdlist = anim.generate_nucmer_commands(infiles, args.outdirname,
                                                nucmer_exe=args.nucmer_exe,
                                                maxmatch=args.maxmatch)
        logger.info("NUCmer commands:\n" + os.linesep.join(cmdlist))
        if args.scheduler == 'multiprocessing':
            logger.info("Running jobs with multiprocessing")
            cumval = multiprocessing_run(cmdlist, verbose=args.verbose)
            logger.info("Cumulative return value: %d" % cumval)
            if 0 < cumval:
                logger.warning("At least one NUCmer comparison failed. " +
                               "ANIm may fail.")
            else:
                logger.info("All multiprocessing jobs complete.")
        else:
            logger.info("Running jobs with SGE")
            raise NotImplementedError
    else:
        logger.warning("Skipping NUCmer run (as instructed)!")

    # Process resulting .delta files
    logger.info("Processing NUCmer .delta files.")
    try:
        data = anim.process_deltadir(args.outdirname, org_lengths)
    except ZeroDivisionError:
        logger.error("One or more NUCmer output files has a problem.")
        if not args.skip_nucmer:
            if 0 < cumval:
                logger.error("This is possibly due to NUCmer run failure, " +
                             "please investigate")
            else:
                logger.error("This is possibly due to a NUCmer comparison " +
                             "being too distant for use. Please consider " +
                             "using the --maxmatch option.")
        logger.error(last_exception())
    return data


# Calculate ANIb for input
def unified_anib(infiles, org_lengths):
    """Calculate ANIb for files in input directory.

    - infiles - paths to each input file
    - org_lengths - dictionary of input sequence lengths, keyed by sequence

    Calculates ANI by the ANIb method, as described in Goris et al. (2007)
    Int J Syst Evol Micr 57: 81-91. doi:10.1099/ijs.0.64483-0. There are
    some minor differences depending on whether BLAST+ or legacy BLAST
    (BLASTALL) methods are used.

    All FASTA format files (selected by suffix) in the input directory are
    used to construct BLAST databases, placed in the output directory.
    Each file's contents are also split into sequence fragments of length
    options.fragsize, and the multiple FASTA file that results written to
    the output directory. These are BLASTNed, pairwise, against the
    databases.

    The BLAST output is interrogated for all fragment matches that cover
    at least 70% of the query sequence, with at least 30% nucleotide
    identity over the full length of the query sequence. This is an odd
    choice and doesn't correspond to the twilight zone limit as implied by
    Goris et al. We persist with their definition, however.  Only these
    qualifying matches contribute to the total aligned length, and total
    aligned sequence identity used to calculate ANI.

    The results are processed to give matrices of aligned sequence length
    (aln_lengths.tab), similarity error counts (sim_errors.tab), ANIs
    (perc_ids.tab), and minimum aligned percentage (perc_aln.tab) of
    each genome, for each pairwise comparison. These are written to the
    output directory in plain text tab-separated format.
    """
    logger.info("Running %s" % args.method)
    # Build BLAST databases and run pairwise BLASTN
    if not args.skip_blastn:
        # Make sequence fragments
        logger.info("Fragmenting input files, and writing to %s" %
                    args.outdirname)
        # Fraglengths does not get reused with BLASTN
        fragfiles, fraglengths = anib.fragment_FASTA_files(infiles,
                                                           args.outdirname,
                                                           args.fragsize)
        # Export fragment lengths as JSON, in case we re-run BLASTALL with
        # --skip_blastn
        if args.method == "ANIblastall":
            with open(os.path.join(args.outdirname,
                                   'fraglengths.json'), 'w') as outfile:
                json.dump(fraglengths, outfile)

        # Which executables are we using?
        if args.method == "ANIblastall":
            blastdb_exe = args.formatdb_exe
            blastn_exe = args.blastall_exe
        else:
            blastdb_exe = args.makeblastdb_exe
            blastn_exe = args.blastn_exe

        # Build BLASTN databases
        logger.info("Constructing %s BLAST databases" % args.method)
        cmdlist = anib.generate_blastdb_commands(infiles, args.outdirname,
                                                 blastdb_exe=blastdb_exe,
                                                 mode=args.method)
        logger.info("Generated commands:\n%s" % '\n'.join(cmdlist))
        if args.scheduler == 'multiprocessing':
            logger.info("Running jobs with multiprocessing")
            cumval = multiprocessing_run(cmdlist, verbose=args.verbose)
            if 0 < cumval:
                logger.warning("At least one makeblastdb run failed. " +
                               "%s may fail." % args.method)
            else:
                logger.info("All multiprocessing jobs complete.")
        else:
            logger.info("Running jobs with SGE")
            raise NotImplementedError

        # Run pairwise BLASTN
        logger.info("Running %s BLASTN jobs" % args.method)
        cmdlist = anib.generate_blastn_commands(fragfiles, args.outdirname,
                                                blastn_exe, mode=args.method)
        logger.info("Generated commands:\n%s" % '\n'.join(cmdlist))
        if args.scheduler == 'multiprocessing':
            logger.info("Running jobs with multiprocessing")
            cumval = multiprocessing_run(cmdlist, verbose=args.verbose)
            logger.info("Cumulative return value: %d" % cumval)
            if 0 < cumval:
                logger.warning("At least one BLASTN comparison failed. " +
                               "%s may fail." % args.method)
            else:
                logger.info("All multiprocessing jobs complete.")
        else:
            logger.info("Running jobs with SGE")
            raise NotImplementedError
    else:
        # Import fragment lengths from JSON
        if args.method == "ANIblastall":
            with open(os.path.join(args.outdirname, 'fraglengths.json'),
                      'rU') as infile:
                fraglengths = json.load(infile)
        else:
            fraglengths = None
        logger.warning("Skipping BLASTN runs (as instructed)!")

    # Process pairwise BLASTN output
    logger.info("Processing pairwise %s BLAST output." % args.method)
    try:
        data = anib.process_blast(args.outdirname, org_lengths,
                                  fraglengths=fraglengths, mode=args.method)
    except ZeroDivisionError:
        logger.error("One or more BLAST output files has a problem.")
        if not args.skip_blastn:
            if 0 < cumval:
                logger.error("This is possibly due to BLASTN run failure, " +
                             "please investigate")
            else:
                logger.error("This is possibly due to a BLASTN comparison " +
                             "being too distant for use.")
        logger.error(last_exception())
    return data