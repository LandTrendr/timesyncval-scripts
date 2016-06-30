'''
filterAllNBR.py
'''

from lthacks.lthacks import *
from numpy.lib.recfunctions import append_fields
import math, sys, os
import numpy as np

def main(inputCsv, outputCsv, startYear, endYear):
	
	#POPULATE UIDs
	
	uidOutput = os.path.splitext(inputCsv)[0] + "_uid_scaled.csv"
	
	if os.path.exists(uidOutput):
		uidData = csvToArray(uidOutput)
		
	else:

		#extract CSV data
		print "\nreading input data..."
		inputData = csvToArray(inputCsv)
	
		print "\nfiltering data..."
		cond1 = (inputData['FMASK']=='0')
		cond2 = (inputData['DAY'] >= 183)
		cond3 = (inputData['DAY'] <= 244)
		cond4 = (np.logical_not(np.isnan(inputData['NBR'])))
		inds = np.where(cond1 & cond2 & cond3 & cond4)
		filteredData = inputData[inds]
	
		#add UID & scaled NBR to input CSV
		headers = ['UID', 'NBR_SCALED']
		dtypes = ['a32', 'f8']
		uidData = append_fields(filteredData, headers, data=[np.zeros(filteredData.size) for i in headers], dtypes=dtypes)

		#loop thru input CSV rows & populate new fields
		numrows = uidData.size
		print numrows, " found."
		print "\npopulating additional fields..."
		for rownum, row in enumerate(uidData):

			if (rownum%1000 == 0): 
				print "row {0} of {1}...".format(rownum,numrows)
			
			id = str(row["ID"])
			uid = str(int(id[:-3])) + "_" + str(int(id[-3:]))
			uidData["UID"][rownum] = uid
		
			if np.isnan(row['NBR']):
				uidData['NBR_SCALED'][rownum] = 0
			else:
				uidData['NBR_SCALED'][rownum] = row['NBR']*1000
		
		arrayToCsv(uidData, uidOutput)

	
	#create CSV with just 1 NBR value per year
	#use good single image closest to target day 215
	
	uids = np.unique(uidData['UID'])
	years = range(startYear, endYear+1)
	
	headers = ["UID", "YEAR", "NBR_SCALED_TARGET"]
	dtypes = ["a32", "i8", "f8"]
	outputData = np.zeros(uids.size*len(years), dtype=zip(headers,dtypes))
	
	outputData["UID"] = np.repeat(uids, len(years))
	outputData["YEAR"] = np.tile(years, uids.size)
	
	#calculate yearly NBR
	numrows = outputData.size
	print numrows, " found."
	print "\ncalculating yearly NBR..."
	for rownum, row in enumerate(outputData):
	
		if rownum%1000 == 0: 
			print "row {0} of {1}...".format(rownum,numrows)
			if rownum!=0: 
				print outputData['NBR_SCALED_TARGET'][rownum-1]
		
		uid = row['UID']
		year = row['YEAR']
		
		uid_inds = np.where( (uidData['UID'] == uid) & (uidData['YEAR'] == year) )[0]
		
		if len(uid_inds) == 0:
			
			outputData['NBR_SCALED_TARGET'][rownum] = 0
			
		else:
		
			#find closest day to target day
			days = uidData['DAY'][uid_inds]
			diffs = [abs(d-215) for d in days]
			closest_ind = uid_inds[diffs.index(min(diffs))]
		
			target_nbr = uidData['NBR_SCALED'][closest_ind]
			outputData['NBR_SCALED_TARGET'][rownum] = target_nbr

	arrayToCsv(outputData, outputCsv)
		

if __name__ == '__main__': 
	args = sys.argv
	#print args
	sys.exit(main(args[1], args[2], int(args[3]), int(args[4])))
