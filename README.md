# Usage 

`ANI_calculator.py [-h] [-d DOWNLOADTOKEN] [-o OUTDIRNAME] [-i INDIRNAME] [-m METHOD]`

# Description 

This program performs a given ANI method (ANIb or ANIm) on a set of input files or downloads a group of files by syncronizing to `ftp://ftp.ncbi.nlm.nih.gov/genomes/Bacteria/` and by searching for the *DOWNLOADTOKEN*

optional arguments:
 
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

`python ANI_calculator.py -d Haemophilus_influenzae -o output -c False -t ANIm`

Downloads all the *fna* files from *Haemophilus influenzae* and then runs the *ANIm* method. The results will go to the *output* directory.
