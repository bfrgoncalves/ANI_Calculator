import subprocess
import argparse
import os
import shutil
from os import listdir
from os.path import isfile, join


def main():

	parser = argparse.ArgumentParser(description="This program performs the ANI method (ANIb or ANIm)")
	parser.add_argument('-i', nargs='?', type=str, help="folder with fna files", required=True)
	parser.add_argument('-o', nargs='?', type=str, help='Destination folder', required=True)
	parser.add_argument('-c', nargs='?', type=bool, help="is cluster version", required=True)
	parser.add_argument('-t', nargs='?', type=str, help="type of ANI (ANIm or ANIb)", required=True)

	args = parser.parse_args()

	fnaGenomes = args.i
	ANIout = args.o
	isCluster = args.c
	typeANI = args.t

	if args.c:
		nonCluster(args)
	else:
		cluster(args)


def nonCluster(args):
	print 'Running'
	subprocess.call(['python', 'pyani_version2/average_nucleotide_identity.py','-i', args.i, '-o',  args.o,  '-m', args.t]);


def cluster(args):
	print 'cluster version'