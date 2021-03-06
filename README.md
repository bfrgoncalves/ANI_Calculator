# Usage 

`ANI_calculator.py [-h] [-d DOWNLOADTOKEN] [-o OUTDIRNAME] [-i INDIRNAME] [-m METHOD]`

# Description 

This program performs a given ANI method (ANIb or ANIm) on a set of input files or downloads a group of files by syncronizing to `ftp://ftp.ncbi.nlm.nih.gov/genomes/Bacteria/` and by searching for the *DOWNLOADTOKEN*

ANIb method: Richter et al (2009) Proc Natl Acad Sci USA 106: 19126-19131 doi:10.1073/pnas.0906412106

ANIm method: Goris et al. (2007) Int J Syst Evol Micr 57: 81-91. doi:10.1099/ijs.0.64483-0

Optional arguments:
 
  -h show this help message and exit

  -d DOWNLOADTOKEN 
  			Token to search at ftp://ftp.ncbi.nlm.nih.gov/genomes/Bacteria/

  -o OUTDIRNAME 
  			Output directory
  
  -i INDIRNAME INDIRNAME
            Input directory name
  
  -m METHOD
  			Method to use (ANIm or ANIb)

# Example of usage

*ANIm* analysis after downloading from NCBI files with *Haemophilus_influenzae* token: `python ANI_calculator.py -d Haemophilus_influenzae -o output -t ANIm`

*ANIb* analysis using files from *InpuFiles* folder: `python ANI_calculator.py -i InputFiles -o output -t ANIb`


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
