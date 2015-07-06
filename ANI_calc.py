#!/usr/bin/python
from ANI_functions import func_ANI_calc
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


	def ANI_calc(args):
	    ANI_results = func_ANI_calc(args[0], args[1], args[2], args[3], args[4])

	    final =	(args[0], ANI_results)

	    filepath=os.path.join(temppath , str(args[4]) +"ANIcalc_result.txt")

	    with open(filepath, 'wb') as f:
			pickle.dump(final, f)

	    return True


	ANI_calc(argumentList)

if __name__ == "__main__":
    main()