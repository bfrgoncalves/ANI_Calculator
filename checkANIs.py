import os
import shutil
from os import listdir
from os.path import isfile, join, isdir
import sys
import csv
import argparse

def checkANI(args):
	
	rownum = 0
	highANI = []
	lowANI = []
	toList = {}
	toListl = {}
	countHigh = 0
	countLow = 0

	with open(args.i, 'rb') as f:
		reader = csv.reader(f, delimiter='\t')
		for row in reader:
			# Save header row.
			if rownum == 0:
				header = row
			else:
				rowLabel = row[0]
				token = rowLabel.split('_')[0:2]
				token = '_'.join(token)
				for colnum in range(1, len(row)-1):
					if float(row[colnum]) >= 0.96 and token not in header[colnum]:
						try:
							if toList[str(rowLabel+'--'+header[colnum])]:
								print 'Already at highANIlist'	
						except KeyError:
							try:
								if toList[str(header[colnum]+'--'+rowLabel)]:
									print 'Already at highANIlist'
							except KeyError:
								highANI.append([rowLabel, header[colnum], row[colnum]])
								countHigh += 1
								toList[rowLabel+'--'+header[colnum]] = True
					elif float(row[colnum]) < 0.95 and token in header[colnum]:
						try:
							if toListl[str(rowLabel+'--'+header[colnum])]:
								print 'Already at lowANIlist'	
						except KeyError:
							try:
								if toListl[str(header[colnum]+'--'+rowLabel)]:
									print 'Already at lowANIlist'
							except KeyError:
								lowANI.append([rowLabel, header[colnum], row[colnum]])
								countLow += 1
								toListl[rowLabel+'--'+header[colnum]] = True


			rownum += 1

	
	return highANI, lowANI, countHigh, countLow

def constructFile(hANI, lANI, countHigh, countLow):
	lf = open(os.path.join(os.getcwd(), 'ANIresults_high95DS.tab'), 'w')
	lf.write('Query\tTarget\tValue\n')
	for i in hANI:
		lf.write(i[0] + '\t' + i[1] + '\t' + i[2] + '\n')
	lf.close()
	
	lf = open(os.path.join(os.getcwd(), 'ANIresults_low95SS.tab'), 'w')
	lf.write('Query\tTarget\tValue\n')
	for i in lANI:
		lf.write(i[0] + '\t' + i[1] + '\t' + i[2] + '\n')
	lf.close()



def main():

	parser = argparse.ArgumentParser(description="This program checks for high and low values of ANI between and in the same species using the row names")
	parser.add_argument('-i', nargs='?', type=str, help="Matrix file", required=True)

	args = parser.parse_args()

	hANI, lANI, countHigh, countLow = checkANI(args)

	constructFile(hANI, lANI, countHigh, countLow)

if __name__ == "__main__":
    main()