#!/usr/bin/python
import subprocess
import argparse
import os
import shutil
from os import listdir
from os.path import isfile, join, isdir
from datetime import datetime

from cluster_utils import create_pickle, create_Jobs
import pickle


def main():

	parser = argparse.ArgumentParser(description="This program performs the ANI method (ANIb or ANIm)")
	parser.add_argument('-n', nargs='?', type=str, help="Results identifier", required=False)
	parser.add_argument('-i', nargs='?', type=str, help="folder with fna files", required=False)
	parser.add_argument('-d', nargs='?', type=str, help="Token to download from NCBI/Bacteria", required=False)
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
	
	
	if args.i:
		currentDir = os.getcwd()
		inputDir = os.path.join(currentDir, args.i)
	else:
		currentDir = os.getcwd()
		inputDir = os.path.join(currentDir,'InputFiles')
		listOfArgs = (args.d, inputDir, '*.fna')
		print listOfArgs
		action = 'dwnFTP'
		job_args, allQueryBasePaths = create_pickle(listOfArgs, inputDir, job_args, action, args.d, allQueryBasePaths, 1)
		print job_args, allQueryBasePaths
		create_Jobs(job_args, 'dwnFTP_cluster.py', allQueryBasePaths)

	onlyfiles = [ f for f in listdir(inputDir) if isfile(join(inputDir,f)) ]

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
	finalResults.append(onlyfiles)

	for i in onlyfiles:
		toAppend = []
		toAppend.append(i)
		for j in onlyfiles:
			tocheck1 = i.split('.')[0]
			tocheck2 = j.split('.')[0]
			toAppend.append(dictOfResults[tocheck1][0][tocheck2])
		finalResults.append(toAppend)

	if not os.path.isdir(args.o):
		os.makedirs(args.o)

	resultFileName = 'results_' + str(args.n) + '_' + str(datetime.now()) + '.tab'
	
	lf=open(os.path.join(str(args.o), resultFileName),'w')
	lf.write('\t')
	for i in finalResults:
		lf.write('\t'.join([str(x) for x in i]))
		lf.write('\n')

	lf.close()

if __name__ == "__main__":
    main()