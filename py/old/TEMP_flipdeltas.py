import os, sys
import numpy as np
from lthacks.lthacks import *
from numpy.lib.recfunctions import append_fields
import math


def calcDeltas(alignedData,startYear):

	print "\nCalculating Deltas..."

	#append delta columns
	alignedData = append_fields(alignedData, ['D_FLIP_RAW', 'D_FLIP_FTV'], data=[np.zeros(alignedData.size), 
	np.zeros(alignedData.size)], dtypes=['f8', 'f8'])

	rowsToDelete = np.where(alignedData['YEAR'] == startYear)
	
	for r,row in enumerate(alignedData):
		
		if r == 0:
			continue
	
		alignedData['D_FLIP_RAW'][r] = row['FLIP_RAW'] - alignedData['FLIP_RAW'][r-1]
		alignedData['D_FLIP_FTV'][r] = row['FLIP_FTV'] - alignedData['FLIP_FTV'][r-1]
		
	alignedData = np.delete(alignedData, rowsToDelete)
	
	print "\t Done!"
	
	return alignedData
	
	
def main(summary_csv, output_csv):

	summary_data = csvToArray(summary_csv)
	
	output_data = calcDeltas(summary_data, 1985)
	
	arrayToCsv(output_data, output_csv)
	
	
if __name__ == '__main__': 
    args = sys.argv
    sys.exit(main(args[1], args[2]))
    
    