#!/usr/bin/python

def createStatusFile(filepath, arrayOfStatus):
	#[0] token
	#[1] download time
	#[2] number of dirs checked
	#[3] number of downloaded files
	#[4] number of files under 1MB
	#[5] ANI time
	#[6] total time

	lf=open(os.path.join(filepath,'w')
	lf.write('Results: \n\n')
	lf.write('Token: ' + str(arrayOfStatus[0]) + '\n')
	lf.write('Download Time: ' + str(arrayOfStatus[1]) + '\n')
	lf.write('Dirs checked: ' + str(arrayOfStatus[2]) + '\n')
	lf.write('Number of downloaded files: ' + str(arrayOfStatus[3]) + '\n')
	lf.write('Number of files under 1MB: ' + str(arrayOfStatus[4]) + '\n')
	lf.write('ANI Time: ' + str(arrayOfStatus[5]) + '\n')
	lf.write('Total Time: ' + str(arrayOfStatus[5]) + '\n')

	lf.close()


def createMatrixFile(filepath, finalResults):

	lf=open(os.path.join(filepath,'w')
	lf.write('\t')
	for i in finalResults:
		lf.write('\t'.join([str(x) for x in i]))
		lf.write('\n')

	lf.close()