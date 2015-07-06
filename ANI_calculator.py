#!/usr/bin/python
import subprocess
import argparse
import os
import shutil
from os import listdir
from os.path import isfile, join, isdir

from cluster_utils import create_pickle, create_Jobs


def main():

	parser = argparse.ArgumentParser(description="This program performs the ANI method (ANIb or ANIm)")
	parser.add_argument('-i', nargs='?', type=str, help="folder with fna files", required=False)
	parser.add_argument('-d', nargs='?', type=str, help="Token to download from NCBI/Bacteria", required=True)
	parser.add_argument('-s', nargs='?', type=bool, help="Directory for downloaded data", required=False)
	parser.add_argument('-o', nargs='?', type=str, help='Destination folder', required=True)
	parser.add_argument('-t', nargs='?', type=str, help="type of ANI (ANIm or ANIb)", required=True)

	args = parser.parse_args()

	cluster(args)


def cluster(args):
	print 'Running cluster version'
	
	job_args = []
	allQueryBasePaths = []
	
	if not os.path.isdir(os.path.join(os.getcwd(),'InputFiles')):
		os.makedirs(os.path.join(os.getcwd(),'InputFiles'))
	
	
	currentDir = os.getcwd()
	inputDir = os.path.join(currentDir,'InputFiles')
	listOfArgs = (args.d, inputDir, '*.fna')
	print listOfArgs
	action = 'dwnFTP'
	job_args, allQueryBasePaths = create_pickle(listOfArgs, inputDir, job_args, action, args.d, allQueryBasePaths)
	print job_args, allQueryBasePaths
	create_Jobs(job_args, 'dwnFTP_cluster.py', allQueryBasePaths)

	onlyfiles = [ f for f in listdir(inputDir) if isfile(join(inputDir,f)) ]

	for i in onlyfiles:
		for j in onlyfiles:
			nameI = i.split('.')[0]
			nameJ = i.split('.')[0]
			fullName = nameI + '_vs_' + nameJ
			if not os.path.isdir(os.path.join(inputDir,fullName)):
				print "Dir not found. Creating it..."
				os.makedirs(os.path.join(inputDir,fullName))

	########## FAZER PARTE DO ANI ##############################


if __name__ == "__main__":
    main()