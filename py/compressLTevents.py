'''
compressLTevents.py

inputs: 
	- kernel prefix
	- path to summary csv
	- output path
	
output:
	- expanded summary csv with compressed kernels
'''

from lthacks.lthacks import *
import numpy as np
import os, sys, math


def main(inputPath, kernelPrefix, outputPath):
	
	#read input summary data
	outputData = csvToArray(inputPath)
	
	#extract fields from inputCsv that start with kernelPrefix
	kernelFields = list(filter(lambda x: x.startswith(kernelPrefix.upper()), 
	outputData.dtype.names))
	
	#define a total magnitude field to be calculated in output
	totalField = "TOTALMAG_" + kernelPrefix.upper()
	
	#define all fields to added in output, includes compressed version of kernel fields
	compressedFields = ["COMPRESSED_"+i for i in kernelFields]
	meanField = "MEAN_COMPRESSED_"+kernelPrefix
	medianField = "MEDIAN_COMPRESSED_"+kernelPrefix
	maxField = "MAX_COMPRESSED_"+kernelPrefix
	addFields = [totalField] + ["YOD_BOOL"] + compressedFields + [meanField, medianField, maxField]
	
	#append all additional fields to output data array
	outputData = append_fields(outputData, addFields, data=[np.zeros(outputData.size, dtype='i8') for i in addFields])
	
	#calculate total magnitude field
	outputData[totalField] = [sum(outputData[kernelFields][i]) for i in range(outputData.size)]
	
	#get all plotid's
	plotIds = np.unique(outputData['PLOTID'])
	
	#loop thru plot id's
	for idNum,id in enumerate(plotIds):
	
		#iteratively find maximum magnitude field among all years 
		#add previous year kernel & next year kernel to the max year kernel
		#save this as in the "compressed" kernel fields
		#once those 3 years have been manipulated, mark them to exclude from next iteration
		#do this until all years have been marked or all remaining magnitudes are 0's
	
		idInds = np.where(outputData['PLOTID'] == id) #at this point all 'YOD_BOOLS' should be 0
		idRows = outputData[idInds]
		
		#get max magnitude
		maxMag = np.max(idRows[totalField])
		
		while (idRows.size > 0) and (maxMag > 0):
		
			#get max magnitude year
			maxYear = idRows['IMAGE_YEAR'][idRows[totalField] == maxMag][0] #take 1st year if 2 years with the same max value
		
			#mark YOD with 1
			maxInd = np.where((outputData['PLOTID'] == id) & (outputData['IMAGE_YEAR'] == maxYear))[0][0]
			outputData['YOD_BOOL'][maxInd] = 1
		
			#mark surrounding years with -1
			addKernels = [outputData[kernelFields][maxInd]]
			if (maxInd - 1) in idInds[0]: 
				outputData['YOD_BOOL'][maxInd-1] = -1
				addKernels.append(outputData[kernelFields][maxInd-1])
			if (maxInd + 1) in idInds[0]: 
				outputData['YOD_BOOL'][maxInd+1] = -1
				addKernels.append(outputData[kernelFields][maxInd+1])
		
			#populate compressed kernel
			compressedKernel =[sum(x) for x in zip(*addKernels)]
			for f,k in zip(compressedFields,compressedKernel):
				outputData[f][maxInd] = k				
			
			#find remaining indices to compare
			idInds = np.where((outputData['PLOTID'] == id) & (outputData['YOD_BOOL'] == 0))
			idRows = outputData[idInds]
			
			#get max magnitude
			maxMag = np.max(idRows[totalField])
			
	#populate mean & median & max of compressed kernel
	for ind,row in enumerate(outputData):

		data = [int(i) for i in outputData[compressedFields][ind]]
	
		outputData[meanField][ind] = np.mean(data)
		outputData[medianField][ind] = np.median(data)
		outputData[maxField][ind] = np.max(data)
	
	#save output data		
	arrayToCsv(outputData, outputPath)
		
		
if __name__ == '__main__': 	
	args = sys.argv
	
	if (len(args) == 4):
		
		sys.exit(main(*args[1:]))
		
	else:
	
		usage = "python compressLTevents.py {path_to_summarize_csv} {kernel_prefix} \
		{output_path}"
		sys.exit("Invalid number of arguments. \nUsage: " + usage)


  