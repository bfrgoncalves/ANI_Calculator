#!/usr/bin/python
from dwn_functions import func_dwnFTP
import sys
import pickle
import os

def main():

	try:
		input_file = sys.argv[1]
		temppath = sys.argv[2]
	except IndexError:
		print "usage: list_pickle_obj"

	argumentList=[]
	
	print type(input_file)
	print input_file
	with open(input_file,'rb') as f:
		argumentList = pickle.load(f)


	def dwnFTP_cluster(args):
	    fileNames = func_dwnFTP(args[0], args[1], args[2])

	    final =	(args[0], fileNames)

	    filepath=os.path.join(temppath , str(args[1])+"_FTP_result.txt")

	    with open(filepath, 'wb') as f:
			pickle.dump(final, f)

	    return True


	dwnFTP_cluster(argumentList)

if __name__ == "__main__":
    main()