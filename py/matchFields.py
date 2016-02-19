from lthacks.lthacks import *
import numpy as np
from numpy.lib.recfunctions import append_fields

def main(inputCsv, matchCsv, addColumn, matchColumn, outputCsv):

	inputData = csvToArray(inputCsv)
	
	matchData = csvToArray(matchCsv)
	
	# append field to data array
	outputData = inputData
	outputData = append_fields(outputData, [addColumn.upper()], 
							   data=[np.zeros(outputData.size)], 
							   dtypes=["a25"])
							   
	for iter, row in enumerate(outputData):
		
		id = row[matchColumn]
		matchInd = np.where(matchData[matchColumn] == id)[0][0]
		
		outputData[iter][addColumn] = matchData[matchInd][addColumn]
		
		
	arrayToCsv(outputData, outputCsv)
	
if __name__ == '__main__': 	
	args = sys.argv
		
	if (len(args) == 6):
		sys.exit(main(*args[1:]))
	
	else:
		usage = "python matchField.py {path_to_inputdata_csv} \
		 {path_to_match_csv} {column_to_add} {id_column} {output_csv}"
		sys.exit("Invalid number of arguments. \nUsage: " + usage)
		
	
	
	
	
	
	