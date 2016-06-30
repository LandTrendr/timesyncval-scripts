'''
converting EE LT outputs to summary table format
'''
import os, sys
import numpy as np
from lthacks.lthacks import *
from numpy.lib.recfunctions import append_fields
import math
    
def stretchNationalTS(interpData):

	print "\nStretching Timesync data into yearly format..."

	startYear = int(np.min(interpData['START_YEAR']))
	endYear = int(np.max(interpData['END_YEAR']))
	
	#define stretched data array
	headers = ["UID", "PLOTID", "TSA", "YEAR", "CHANGE_PROCESS"]
	types = ["a32", "i8", "i8", "i8", "a32"]
	years = range(startYear, endYear+1)
	uids = np.unique(interpData['UID'])
	stretchedData = np.zeros(len(years)*uids.size, dtype=zip(headers,types))
	
	#populate all columns except CHANGE PROCESS
	split_uids = np.array([i.split("_") for i in uids])
	tsas = split_uids[:,0]
	plotids = split_uids[:,1]

	stretchedData['UID'] = np.repeat(uids, len(years))
	stretchedData['PLOTID'] = np.repeat(plotids, len(years))
	stretchedData['TSA'] = np.repeat(tsas, len(years))
	stretchedData['YEAR'] = np.tile(years, uids.size)
	
	for row in interpData:
	
		try: 
		
			uid = row['UID']
			startYear = row['START_YEAR']
			endYear = row['END_YEAR']
		
			for year in range(startYear+1,endYear+1):
		
				stretchedRow = np.where( (stretchedData['UID']==uid) & (stretchedData['YEAR']==year) )[0][0]
				stretchedData['CHANGE_PROCESS'][stretchedRow] = row['CHANGE_PROCESS']
				
		except IndexError:
			print row
		
	print "\tDone!"
	
	return stretchedData


def stretchLTEE(interpData):

	print "\nStretching LandTrendr data into yearly format..."
	
	startYear = int(np.min(interpData['YOD1'][~np.isnan(interpData['YOD1'])]))
	endYear = int(np.max(interpData['YOD2'][~np.isnan(interpData['YOD1'])]))

	#define stretched data array
	headers = ["UID", "PLOTID", "TSA", "X", "Y", "YEAR", "RAW", "FTV"]
	types = ["a32", "i8", "i8", "f8", "f8", "i8", "f8", "f8"]
	years = range(startYear, endYear+1)
	stretchedData = np.zeros(len(years)*interpData.size, dtype=zip(headers,types))
	
	#populate all columns except ROW & FTV
	uids = interpData['UID']
	tsas = interpData['TSA']
	plotids = interpData['PLOTID']
	xs= interpData['X']
	ys= interpData['Y']
	
	stretchedData['UID'] = np.repeat(uids, len(years))
	stretchedData['PLOTID'] = np.repeat(plotids, len(years))
	stretchedData['TSA'] = np.repeat(tsas, len(years))
	stretchedData['X'] = np.repeat(xs, len(years))
	stretchedData['Y'] = np.repeat(ys, len(years))
	stretchedData['YEAR'] = np.tile(years, uids.size)
	
	#define year column names from interpData (vertex years)
	yearCols = ["YOD"+str(i) for i in range(1,8)]
	
	#loop thru interpData rows & populate RAW & FTV columns in stretchedData
	for row in interpData:
		
		prevYear, prevRow, prevRaw, prevFtv = (None,)*4 #reset for each plot
		
		for y,yearCol in enumerate(yearCols):
		
			yearNum = str(y+1)
			
			if (row[yearCol] == 0) or math.isnan(row[yearCol]):
				break
				
			else:
				newYear = int(row[yearCol])
				stretchedRow = np.where( (stretchedData['UID']==row['UID']) & (stretchedData['YEAR']==newYear) )[0][0]

				newRaw, newFtv = (row["RAW"+yearNum], row["FTV"+yearNum])
				stretchedData['RAW'][stretchedRow] = newRaw
				stretchedData['FTV'][stretchedRow] = newFtv
				
				#interpolate between current year and previous year
				if prevYear:

					rawSlope = (newRaw - prevRaw) / (newYear - prevYear)
					ftvSlope = (newFtv - prevFtv) / (newYear - prevYear)
					
					rawIntercept = prevRaw - (rawSlope*prevYear)
					ftvIntercept = prevFtv - (ftvSlope*prevYear)
					
					for interpIter,interpYear in enumerate(range(prevYear+1, newYear)):
		
						interpRow = prevRow + interpIter + 1
						stretchedData['RAW'][interpRow] = rawSlope*interpYear + rawIntercept
						stretchedData['FTV'][interpRow] = ftvSlope*interpYear + ftvIntercept
				
				prevYear, prevRow, prevRaw, prevFtv = (newYear, stretchedRow, newRaw, newFtv)

	print "\tDone!"
				
	return stretchedData
	
	
def alignYearlyDatasets(ltData, tsData, startYear, endYear):

	print "\nAligning yearly Timesync & LandTrendr data into one CSV..."
	
	#remove LT rows not in desired timeframe
	discardYears = np.where( (ltData['YEAR'] > endYear) | (ltData['YEAR'] < startYear) )
	
	ltData = np.delete(ltData, discardYears)
	
	#append CHANGE_PROCESS column to ltData
	alignedData = append_fields(ltData, ['CHANGE_PROCESS'], data=[np.zeros(ltData.size)], dtypes=['a32'])
	
	
	rowsToDelete = []
	#loop thru ltData and append CHANGE_PROCESS info from tsData
	for r,row in enumerate(alignedData):
	
		uid = row['UID']
		year = row['YEAR']
		
		try:
			tsIndex = np.where( (tsData['UID'] == uid) & (tsData['YEAR'] == year) )[0][0]
			alignedData['CHANGE_PROCESS'][r] = tsData['CHANGE_PROCESS'][tsIndex]
			
		except IndexError:
			#exclude plots that are not in timesync dataset
			rowsToDelete.append(r)
			continue
		
	alignedData = np.delete(alignedData, rowsToDelete)
	
	print "\tDone!"
	
	return alignedData
	
def calcFlips(alignedData):
	
	print "\nFlipping LT outputs..."
	
	#append delta columns
	alignedData = append_fields(alignedData, ['FLIP_RAW', 'FLIP_FTV'], data=[np.zeros(alignedData.size), 
	np.zeros(alignedData.size)], dtypes=['f8', 'f8'])
	
	for r,row in enumerate(alignedData):
	
		alignedData['FLIP_RAW'][r] = row['RAW'] * -1
		alignedData['FLIP_FTV'][r] = row['FTV'] * -1
		
	print "\t Done!"
	
	return alignedData
	
		
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
	

def main(tsCsv, ltCsv, startYear, endYear, outputCsv):

	#define intermediate output filenames
	ts_output = os.path.splitext(tsCsv)[0] + "_yearly.csv"
	lt_output = os.path.splitext(ltCsv)[0] + "_yearly.csv"

	#stretch timesync interps
	if not os.path.exists(ts_output):
		tsData = csvToArray(tsCsv)
		tsData = stretchNationalTS(tsData)
		arrayToCsv(tsData, ts_output)
	else:
		tsData = csvToArray(ts_output)
	
	#stretch landtrendr outputs
	if not os.path.exists(lt_output):
		ltData = csvToArray(ltCsv)
		ltData = stretchLTEE(ltData)
		arrayToCsv(ltData, lt_output)
	else:
		ltData = csvToArray(lt_output)

	alignedData = alignYearlyDatasets(ltData, tsData, startYear, endYear)
	
	alignedData = calcFlips(alignedData)
	
	alignedData = calcDeltas(alignedData, startYear)
	
	arrayToCsv(alignedData, outputCsv)
	
	

if __name__ == '__main__': 
    args = sys.argv
    sys.exit(main(args[1], args[2], int(args[3]), int(args[4]), args[5]))