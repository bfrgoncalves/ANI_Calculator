# Usage 

`ANI_calculator.py [-h] [-d DOWNLOADTOKEN] [-o OUTDIRNAME] [-i INDIRNAME] [-t METHOD] [-n RESULTSINDENTIFIER] [-s DOWNLOADDIR]`

# Description 

This program performs a given ANI method (ANIb or ANIm) on a set of input files or downloaded files from `ftp://ftp.ncbi.nlm.nih.gov/genomes/Bacteria/` after searching for the *DOWNLOADTOKEN*

Uses the **Distributed Resource Management Application API (DRMMA)** for the submission and control of jobs in a **Cluster**.

ANIm method: Richter et al (2009) Proc Natl Acad Sci USA 106: 19126-19131 doi:10.1073/pnas.0906412106

ANIb method: Goris et al. (2007) Int J Syst Evol Micr 57: 81-91. doi:10.1099/ijs.0.64483-0

Optional arguments:
 
  -h show this help message and exit

  -d DOWNLOADTOKEN (Required = False)
  			Token to search at ftp://ftp.ncbi.nlm.nih.gov/genomes/Bacteria/

  -s DOWNLOADDIR (Required = False)
  			Directory where the downloaded files will be placed

  -o OUTDIRNAME (Required = True)
  			Output directory
  
  -i INDIRNAME (Required = False) 
            Input directory name
  
  -t METHOD (Required = True)
  			Method to use (ANIm or ANIb)

  -n RESULTSIDENTIFIER (Required = True)
  			Token to identify the results

# Example of usage


*ANIm* analysis after downloading from NCBI files with *Haemophilus_influenzae* token: `python ANI_calculator.py -d Haemophilus_influenzae -o output -t ANIm -n Haemophilus`

*ANIb* analysis using files from *InpuFiles* folder: `python ANI_calculator.py -i InputFiles -o output -t ANIb -n Haemophilus`


#Dependencies

For ANI analysis

* Biopython http://www.biopython.org

* NumPy http://www.numpy.org/

* pandas http://pandas.pydata.org/

* SciPy http://www.scipy.org/

* BLAST+ executable in the $PATH, or available on the command line (required for ANIb analysis) ftp://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/LATEST/

* MUMmer executables in the $PATH, or available on the command line (required for ANIm analysis) http://mummer.sourceforge.net/

#Modules used

* dwnFTP https://github.com/jacarrico/dwnFTP

* pyani  https://github.com/widdowquinn/pyani
