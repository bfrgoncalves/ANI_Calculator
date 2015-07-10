#!/usr/bin/python
import subprocess
import argparse
import os
import shutil
from os import listdir
from os.path import isfile, join, isdir
from datetime import datetime


from cluster_utils import create_pickle, create_Jobs
from createStatusFile import createStatusFile, createMatrixFile
import pickle
import sys


def main():

	parser = argparse.ArgumentParser(description="This program performs a given ANI method (ANIb or ANIm) on a set of input files or downloaded files from `ftp://ftp.ncbi.nlm.nih.gov/genomes/Bacteria/` after searching for the *DOWNLOADTOKEN*")
	parser.add_argument('-n', nargs='?', type=str, help="Results identifier", required=True)
	parser.add_argument('-i', nargs='?', type=str, help="Repository for fasta files", required=True)
	parser.add_argument('-d', nargs='?', type=str, help="Token to download from NCBI/Bacteria", required=False)
	parser.add_argument('-s', nargs='?', type=bool, help="Directory for downloaded data", required=False)
	parser.add_argument('-o', nargs='?', type=str, help='Destination folder', required=True)
	parser.add_argument('-t', nargs='?', type=str, help="type of ANI (ANIm or ANIb)", required=True)

	args = parser.parse_args()

	cluster(args)


def cluster(args):
	print 'Running cluster version'

	startTime = datetime.now()
	statusArray = []
	
	job_args = []
	allQueryBasePaths = []
	curDir = os.getcwd()

	if not args.i and not args.d:
		print 'A folder with input files or a token to download from NCBI is required.'
		sys.exit()
	
	if args.i and not os.path.isdir(args.i):
		os.makedirs(args.i)
		print 'Downloading files to ' + args.c
	elif args.c:
		print 'Downloading files to ' + args.c
	if not args.c and not os.path.isdir(os.path.join(os.getcwd(),'InputFiles')):
		os.makedirs(os.path.join(os.getcwd(),'InputFiles'))
	
	
	if args.d:
		currentDir = os.getcwd()
		inputDir = os.path.join(currentDir,args.i)
		if not os.path.isdir(inputDir):
			os.makedirs(inputDir)
		listOfArgs = (args.d, inputDir, '*.fna', 1)
		statusArray.append(args.d)
		action = 'dwnFTP'
		job_args, allQueryBasePaths = create_pickle(listOfArgs, inputDir, job_args, action, args.d, allQueryBasePaths, 1)
		create_Jobs(job_args, 'dwnFTP_cluster.py', allQueryBasePaths)

		countResults = 0
		for i in allQueryBasePaths:
			countResults += 1
			filepath=os.path.join(i, str(countResults)+"_"+ action + "_result.txt")

			with open(filepath,'rb') as f:
				x = pickle.load(f)
			
			statusArray.append(x[0])
			statusArray.append(x[1])
			statusArray.append(x[2])
			statusArray.append(x[3])
	else:
		currentDir = os.getcwd()
		inputDir = os.path.join(currentDir, args.i)
		statusArray.append(args.i)


	timeDownload = datetime.now() - startTime
	startTimeD = datetime.now()

	onlyfiles = [ f for f in listdir(inputDir) if isfile(join(inputDir,f)) ]

	if len(onlyfiles) == 0:
		print 'There are no files in the ' + inputDir + 'directory.'
		sys.exit()

	ComparisonsToMake = []
	countComparisons = 0
	job_args = []
	allQueryBasePaths = []

	countFiles = len(onlyfiles)
	for i in range(0,countFiles-1):
		for j in range(i+1, countFiles):
			ComparisonsToMake.append(onlyfiles[i] + '--' + onlyfiles[j])

	for comparison in ComparisonsToMake:
		countComparisons += 1
		listOfArgs = (inputDir, comparison, args.t, 'multiprocessing', countComparisons)
		action = 'ANIcalc'
		job_args, allQueryBasePaths = create_pickle(listOfArgs, inputDir, job_args, action, comparison, allQueryBasePaths, countComparisons)
	
	create_Jobs(job_args, 'ANI_calc.py', allQueryBasePaths)

	timeANI = datetime.now() - startTimeD

	countResults = 0
	dictOfResults = {}
	for i in allQueryBasePaths:
		countResults += 1
		filepath=os.path.join(i, str(countResults)+"_"+ action + "_result.txt")

		with open(filepath,'rb') as f:
			x = pickle.load(f)

		for i in x[1][1]:
			indexes = x[1][1][i].index.tolist()
			for j in indexes:
				try:
					dictOfResults[i][0][j] = x[1][1][i][j]
				except KeyError:
					dictOfResults[i] = []
					dictOfResults[i].append({})
					dictOfResults[i][0][j] = x[1][1][i][j]


	finalResults = []
	finalResults.append([str(x.split('.')[0]) for x in onlyfiles])

	for i in onlyfiles:
		toAppend = []
		toAppend.append(i.split('.')[0])
		for j in onlyfiles:
			tocheck1 = i.split('.')[0]
			tocheck2 = j.split('.')[0]
			toAppend.append(dictOfResults[tocheck1][0][tocheck2])
		finalResults.append(toAppend)

	if not os.path.isdir(args.o):
		os.makedirs(args.o)

	resultFile = 'results_' + str(args.n) + '_' + str(datetime.now())
	resultFile= resultFile.replace(' ', '')
	resultFile = resultFile.replace(':', '_')
	resultFile = resultFile.replace('.', '_', 1)

	resultFileName = resultFile + '.tab'
	statusFileName = resultFile + '.txt'

	statusArray.append(str(timeANI))
	statusArray.append(str(datetime.now() - startTime))

	createMatrixFile(os.path.join(str(args.o), resultFileName), finalResults)
	createStatusFile(os.path.join(str(args.o), statusFileName), statusArray)

	subprocess.call(['python', 'hierarchical_clustering.py', '--i', os.path.join(str(args.o), resultFileName)])
	
	parsedDir = curDir.split('/')
	del parsedDir[3:]
	homeFolder =  '/'.join([str(x) for x in parsedDir])
	os.chdir(str(homeFolder))
	os.system("rm *py.o*")

	print 'Download Time: ' + str(timeDownload)
	print 'ANI Time: ' + str(timeANI)
	print 'Total Time: ' + str(datetime.now() - startTime)

if __name__ == "__main__":
    main()