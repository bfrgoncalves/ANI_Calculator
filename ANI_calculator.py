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
	#parser.add_argument('-s', nargs='?', type=bool, help="Directory for downloaded data", required=False)
	parser.add_argument('-o', nargs='?', type=str, help='Destination folder', required=True)
	parser.add_argument('-t', nargs='?', type=str, help="type of ANI (ANIm or ANIb)", required=True)
	parser.add_argument('-ci', nargs='?', type=str, help="column input files", required=False)
	parser.add_argument('-ri', nargs='?', type=str, help="row input files", required=False)

	args = parser.parse_args()

	cluster(args)


def cluster(args):
	print 'Running cluster version'

	startTime = datetime.now()
	statusArray = []
	
	job_args = []
	allQueryBasePaths = []
	curDir = os.getcwd()

	if not args.i and not args.d and not args.ci and not args.ri:
		print 'A folder with input files or a token to download from NCBI is required.'
		sys.exit()
	
	if args.d:
		currentDir = os.getcwd()
		inputDir = os.path.join(currentDir,args.i)
		if not os.path.isdir(inputDir):
			os.makedirs(inputDir)
		print 'Downloading files to ' + inputDir
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
		statusArray.append(0)
		statusArray.append('None')
		statusArray.append('None')
		statusArray.append('None')


	timeDownload = datetime.now() - startTime
	startTimeD = datetime.now()


	ComparisonsToMake = []
	countComparisons = 0
	job_args = []
	allQueryBasePaths = []

	if args.ci and args.ri:
		columnonlyfiles = [ f for f in listdir(args.ci) if isfile(join(args.ci,f)) ]
		rowonlyfiles = [ f for f in listdir(args.ri) if isfile(join(args.ri,f)) ]

		for i in columnonlyfiles:
			for j in rowonlyfiles:
				ComparisonsToMake.append(i + '--' + j)

	else:
		onlyfiles = [ f for f in listdir(inputDir) if isfile(join(inputDir,f)) ]

		if len(onlyfiles) == 0:
			print 'There are no files in the ' + inputDir + 'directory.'
			sys.exit()
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

	if args.ci and args.ri:
		finalResults.append([str(x.split('.')[0]) for x in columnonlyfiles])

		for i in rowonlyfiles:
			toAppend = []
			toAppend.append(i.split('.')[0])
			for j in columnonlyfiles:
				tocheck1 = i.split('.')[0]
				tocheck2 = j.split('.')[0]
				toAppend.append(dictOfResults[tocheck1][0][tocheck2])
			finalResults.append(toAppend)
	else:
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