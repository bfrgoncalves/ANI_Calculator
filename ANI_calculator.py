import subprocess
import argparse
import os
import shutil
from os import listdir
from os.path import isfile, join, isdir


def main():

	parser = argparse.ArgumentParser(description="This program performs the ANI method (ANIb or ANIm)")
	parser.add_argument('-i', nargs='?', type=str, help="folder with fna files", required=False)
	parser.add_argument('-d', nargs='?', type=str, help="Token to download from NCBI/Bacteria", required=False)
	parser.add_argument('-o', nargs='?', type=str, help='Destination folder', required=True)
	#parser.add_argument('-c', nargs='?', type=bool, help="is cluster version", required=True)
	parser.add_argument('-t', nargs='?', type=str, help="type of ANI (ANIm or ANIb)", required=True)

	args = parser.parse_args()

	nonCluster(args)

def nonCluster(args):
	print 'Running'
	if not os.path.isdir(os.path.join(os.getcwd(),'InputFiles')):
		os.makedirs(os.path.join(os.getcwd(),'InputFiles'))
	
	if args.d:
		subprocess.call(['python', 'dwnFTP_version2/dwnFTP.py', args.d, 'InputFiles', '*.fna']);
		subprocess.call(['python', 'pyani_version2/average_nucleotide_identity.py','-i', 'InputFiles/' + args.d, '-o',  args.o,  '-m', args.t]);
	else:
		if not args.i:
			print 'Please select the folder with query files'
			os.exit()
		
		subprocess.call(['python', 'pyani_version2/average_nucleotide_identity.py','-i', args.i, '-o',  args.o,  '-m', args.t]);


if __name__ == "__main__":
    main()