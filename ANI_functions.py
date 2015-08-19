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


def func_ANI_calc(InputFilesDir, comparisonToMake, method, scheduler, countComparisons):

    # Have we got a valid method choice?
    # Dictionary below defines analysis function, and output presentation
    # functions/settings, dependent on selected method.


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
        # Schedule NUCmer runs
        if not skip_nucmer:
            cmdlist = anim.generate_nucmer_commands(infiles, outdirname,
                                                    nucmer_exe=nucmer_exe,
                                                    maxmatch=maxmatch)
            if scheduler == 'multiprocessing':
                cumval = multiprocessing_run(cmdlist, verbose=verbose)
            else:
                raise NotImplementedError

        # Process resulting .delta files
        try:
            data = anim.process_deltadir(outdirname, org_lengths)
        except ZeroDivisionError:
            print "One or more NUCmer output files has a problem."
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
        # Build BLAST databases and run pairwise BLASTN
        if not skip_blastn:
            # Make sequence fragments
            # Fraglengths does not get reused with BLASTN
            fragfiles, fraglengths = anib.fragment_FASTA_files(infiles,
                                                               outdirname,
                                                               fragsize)
            # Export fragment lengths as JSON, in case we re-run BLASTALL with
            # --skip_blastn
            if method == "ANIblastall":
                with open(os.path.join(outdirname,
                                       'fraglengths.json'), 'w') as outfile:
                    json.dump(fraglengths, outfile)

            # Which executables are we using?
            if method == "ANIblastall":
                blastdb_exe = pyani_config.FORMATDB_DEFAULT
                blastn_exe = pyani_config.BLASTALL_DEFAULT
            else:
                blastdb_exe = pyani_config.MAKEBLASTDB_DEFAULT
                blastn_exe = pyani_config.BLASTN_DEFAULT

            # Build BLASTN databases
            cmdlist = anib.generate_blastdb_commands(infiles, outdirname,
                                                     blastdb_exe=blastdb_exe,
                                                     mode=method)
            if scheduler == 'multiprocessing':
                cumval = multiprocessing_run(cmdlist, verbose=verbose)
            else:
                raise NotImplementedError

            # Run pairwise BLASTN

            cmdlist = anib.generate_blastn_commands(fragfiles, outdirname,
                                                    blastn_exe, mode=method)
            if scheduler == 'multiprocessing':

                cumval = multiprocessing_run(cmdlist, verbose=verbose)
            else:

                raise NotImplementedError
        else:
            # Import fragment lengths from JSON
            if method == "ANIblastall":
                with open(os.path.join(outdirname, 'fraglengths.json'),
                          'rU') as infile:
                    fraglengths = json.load(infile)
            else:
                fraglengths = None
        try:
            data = anib.process_blast(outdirname, org_lengths,
                                      fraglengths=fraglengths, mode=method)
        except ZeroDivisionError:
            print "One or more BLAST output files has a problem."
        return data

    skip_nucmer = False
    skip_blastn = False
    nucmer_exe = pyani_config.NUCMER_DEFAULT
    maxmatch = False
    verbose = False
    fragsize = pyani_config.FRAGSIZE
    formatdb_exe = pyani_config.FORMATDB_DEFAULT
    blastall_exe = pyani_config.BLASTALL_DEFAULT
    makeblastdb_exe = pyani_config.MAKEBLASTDB_DEFAULT
    blastn_exe = pyani_config.BLASTN_DEFAULT
    outdirname = os.path.join(InputFilesDir, 'Results', comparisonToMake)

    if not os.path.isdir(os.path.join(outdirname)):
        os.makedirs(os.path.join(outdirname))

    methods = {"ANIm": (calculate_anim, pyani_config.ANIM_FILESTEMS),
               "ANIb": (unified_anib, pyani_config.ANIB_FILESTEMS)
              }

    if method not in methods:
        sys.exit(1)

    # Have we got a valid scheduler choice?
    schedulers = ["multiprocessing", "SGE"]
    
    if scheduler not in schedulers:
        sys.exit(1)

    # Get input files
    infiles = []
    infiles.append(os.path.join(InputFilesDir, comparisonToMake.split('--')[0]))
    infiles.append(os.path.join(InputFilesDir, comparisonToMake.split('--')[1]))


    # Get lengths of input sequences
    org_lengths = pyani_files.get_sequence_lengths(infiles)

    # Run appropriate method on the contents of the input directory,
    # and write out corresponding results.
    results = methods[method][0](infiles, org_lengths)

    return results


    