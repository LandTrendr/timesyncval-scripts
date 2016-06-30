'''
LandTrendr Validation with TimeSync interpretations.
This script takes a CSV w/ Aligned TimeSync interpretations & extracted LandTrendr kernels 
w/ summary stats on the LT pixels and creates 2 confusion matrices comparing given 
LT summary stat w/ TS data.

Author: Tara Larrue (tlarrue2991@gmail.com)
'''
import numpy as np
from lthacks.lthacks import *
import datetime

def getTxt(file):
	'''reads parameter file & extracts inputs'''
	
	#open parameter file
	txt = open(file, 'r')
	
	#skip 1st line (title line)
	next(txt)
	
	#define empty parameter dictionary
	parameters = {}

	#loop through parameter file lines & construct parameter dictionary
	for line in txt:
	
		if not line.startswith('#'): #skip commented out lines
			lineitems = line.split(':')
			title = lineitems[0].strip(' \n').lower()
			var = lineitems[1].strip(' \n')
			
			#specify how to read specific parameters
			if title in ['inputcsv', 'modelregion', 'outputpath_yearlybins', 
						 'outputpath_events', 'outputpath_broadcm', 
						 'outputpath_detailedcm']:
						 
				parameters[title] = var
				
			elif title in ['ltcolumn']:
				
				parameters[title] = var.upper()
				
			elif title in ['tolerance']:
				
				parameters[title] = int(var)
				
			elif title in ['lt_bins', 'lt_disturbance_bounds', 'lt_nondisturbance_bounds']:
				
				floats = [float(i.strip()) for i in var.split(",")]
				int_bools = [i.is_integer() for i in floats]
				parameters[title] = [int(f) if b else f for f,b in zip(floats,int_bools)]
				
			elif title in ['ts_disturbances', 'ts_nondisturbances']:
				
				parameters[title] = [i.strip().upper() for i in var.split(",")]
				
			else:
			
				print "\nWARNING: parameter not understood: ", title
						 
	txt.close()
	
	return parameters

def binValidationData(csvData, ltCol, ltbins, matches, plotCol="PLOTID", 
yearCol="IMAGE_YEAR", tsCols=["CHANGE_PROCESS", "RELATIVE_MAGNITUDE"]):
	'''Bins LandTrendr & Timesync data from aligned summary data, outputs new data array'''
	
	print "\nBinning LandTrendr & TimeSync data..."
	
	#define new structured array & populate plot/year data
	dtypes = [(plotCol,'f8'), (yearCol,'f8'), ("TIMESYNC", 'a32'), ("LANDTRENDR", 'a32'), 
	          ("TS_MATCH", 'a32'), ("LT_MATCH", 'a32')]
	binnedArray = np.zeros(csvData.size, dtype=dtypes)
	
	#initialize new array with plot ids and year data
	binnedArray[plotCol] = csvData[plotCol]
	binnedArray[yearCol] = csvData[yearCol]

	#loop thru rows & bin data & populate MATCH columns w/ 'DISTURBANCE'/'NON-DISTURBANCE'
	#TimeSync binned by concatenating change process & relative magitude
	#LandTrendr binned using magnitude LT_BINS defined above
	digitized = np.digitize(csvData[ltCol], ltbins)
	
	for ind,row in enumerate(csvData):
		binnedArray["TIMESYNC"][ind] = str(row[tsCols[0]].upper()) + "_" + \
		str(row[tsCols[1]]) 
		binnedArray["LANDTRENDR"][ind] = str(ltbins[digitized[ind]-1]) + "_" + \
		str(ltbins[digitized[ind]])

		try:
			binnedArray["TS_MATCH"][ind] = matches[binnedArray["TIMESYNC"][ind].upper()]
			binnedArray["LT_MATCH"][ind] = matches[binnedArray["LANDTRENDR"][ind].upper()]
		except KeyError:
			print "WARNING: Skipping ", binnedArray["TIMESYNC"][ind], " ", binnedArray["LANDTRENDR"][ind]
			continue

	print " Done binning."
	return binnedArray

def isMatch(row, col1="TS_MATCH", col2="LT_MATCH"):
	if row[col1] != row[col2]: 
		match = False
	else:
		match = True
	return match

def applyYearTolerance(binnedData, yearTolerance, matches, lt_nondisturbances, 
plotCol="PLOTID", yearCol="IMAGE_YEAR"): 
	'''Bins LandTrendr & Timesync data from aligned CSV data, then creates a '''
	
	print "\nApplying " + str(yearTolerance) + " year tolerance..."
	
	#define new structured array
	altYears = range(1, yearTolerance+1)
	ltAlts = ["LANDTRENDR_ALT{0}".format(k) for k in ["-"+str(i) for i in altYears] + \
	["+"+str(j) for j in altYears]]
	headersToAdd = ltAlts+["LANDTRENDR_FINAL", "LANDTRENDR_FINAL_NOCONSEC"]
	binnedData = append_fields(binnedData, headersToAdd, 
	                           data=[np.zeros(binnedData.size) for i in headersToAdd], 
	                           dtypes='a32')

	#find landtrendr alternatives using yearTolerance
	for ind,row in enumerate(binnedData):
		i = -1
		if (not isMatch(row)) and (row["TS_MATCH"]=="DISTURBANCE"): #ADDED 2nd condition
			for i,alt in enumerate(ltAlts):
				altYear = row[yearCol] + int(alt[-2:])
				#check if alternative year exists
				test = np.where((binnedData[yearCol] == altYear) & 
				                (binnedData[plotCol] == row[plotCol])) 
				if test[0].size != 0: #this cond. won't be met if year is <1984 or >2012
					#populate alternative year column
					binnedData[alt][ind] = binnedData["LANDTRENDR"][test][0] 
					try:
						#change LT_MATCH column based on alternative
						binnedData["LT_MATCH"][ind] = matches[binnedData[alt][ind].upper()] 
					except KeyError:
						continue
				if isMatch(row):
					# binnedData["LANDTRENDR"][ind] = "0" #SHOULD THIS BE HERE???
					break

		#populate LANDTRENDR_FINAL column based on which alternative year for loop was stopped			
		if (i==-1): 
			binnedData["LANDTRENDR_FINAL"][ind] = row["LANDTRENDR"]
			if isMatch(row):
				binnedData["LANDTRENDR"][ind] = "0"
		else:
			if row[alt] == "0.0":
				binnedData["LANDTRENDR_FINAL"][ind] = row["LANDTRENDR"]
			else:
				binnedData["LANDTRENDR_FINAL"][ind] = row[alt]
				#binnedData["LANDTRENDR"][ind + int(alt[-2:])] = "0" #SHOULD THIS BE HERE???

		if (matches[binnedData["LANDTRENDR_FINAL"][ind]] == "DISTURBANCE"):
		
			if ind != 0:
				if (matches[binnedData["LANDTRENDR_FINAL"][ind-1]] == "DISTURBANCE") and \
				(binnedData["LANDTRENDR_FINAL"][ind-1] == binnedData["LANDTRENDR_FINAL"][ind]):
				
					for bin in lt_nondisturbances:
				
						edges = [float(b) for b in bin.split("_")]
					
						if (0 >= edges[0]) and (0 <= edges[1]):
					
							lt_zero_bin = bin
							binnedData["LANDTRENDR_FINAL_NOCONSEC"][ind] = lt_zero_bin
						
				else:
					binnedData["LANDTRENDR_FINAL_NOCONSEC"][ind] = binnedData["LANDTRENDR_FINAL"][ind]
					
			else:
				binnedData["LANDTRENDR_FINAL_NOCONSEC"][ind] = binnedData["LANDTRENDR_FINAL"][ind]
		
		else:
			binnedData["LANDTRENDR_FINAL_NOCONSEC"][ind] = binnedData["LANDTRENDR_FINAL"][ind]
						
	print " Done populating tolerance columns."
	return binnedData

def combineSet(disturbances, magnitudes):
	'''test if possible to combine TimeSync disturbance set into one event'''
	if all([disturbances[0] == i for i in disturbances]): 
		newTS = disturbances[0] + "_" + str(np.mean(magnitudes).astype('int'))
	elif all([((i=="HARVEST") or (i=="SITE-PREPARATION FIRE")) for i in disturbances]):
		newTS = "Harvest_Site-preparation Fire".upper()
	else:
		newTS = None

	return newTS

def isolateEvents(binnedData, plotCol="PLOTID", yearCol="IMAGE_YEAR", tsCol="TIMESYNC"):
	'''Takes in binned yearly data & returns events-only data'''

	print "\nIsolating Disturbance Events..."
	disturbanceInds = np.where((binnedData["TS_MATCH"]=="DISTURBANCE") | 
	                           (binnedData["LT_MATCH"]=="DISTURBANCE"))
	eventsArray = binnedData[disturbanceInds]

	prevRow = None
	consec = [] #initialize set of consecutive disturbances (for 1 plot)
	rowsToDelete = [] #keep track of rows to delete after name combinations are complete
	for ind,row in enumerate(eventsArray):
		#skip first row (nothing to compare to)
		if prevRow:
			#if there are 2+ consec. disturbances for the same plot, capture them
			if (row[plotCol]==prevRow[plotCol]) and (row[yearCol]==(prevRow[yearCol]+1)):
				if not consec: 
					consec.extend([(ind-1,prevRow), (ind,row)])
				else:
					consec.append((ind,row))
				prevRow = row
				continue
			else:
				#if this is the end of a set, run some tests to see how it can be combined
				if consec:
					consec = np.asarray(consec)
					#truth array-which years where TS & LT match
					matches = np.asarray([isMatch(i[1]) for i in consec]) 
					#truth array-which yrs are TS disturbances
					disturbBools = np.asarray([i[1]["TS_MATCH"]=="DISTURBANCE" for i in consec]) 
					#truth array-which yrs are both TS & LT disturbances
					matchingDisturbances = np.logical_and(disturbBools, matches) 
					#TS disturbance call array
					disturbances = np.asarray([i[1][tsCol].split("_")[0].upper() for i in consec]) 
					#TS rel. magnitude call array
					magnitudes = np.asarray([int(i[1][tsCol].split("_")[1].upper()) for i in consec]) 

					try:
						#test if there are some TimeSync disturbances that can be combined
						newTS = combineSet(disturbances[disturbBools], magnitudes[disturbBools]) 

						if any(matchingDisturbances):
							#delete all but 1st matching disturbance row
							rowsToDelete.extend(i[0] for i in consec[~matchingDisturbances]) 
							rowsToDelete.extend(i[0] for i in consec[matchingDisturbances][1:])
							#re-name TimeSync call
							eventsArray[tsCol][consec[matchingDisturbances][0][0]] = newTS 
						else:
							#delete all but 1st row 
							rowsToDelete.extend([i[0] for i in consec[1:]])  
							eventsArray[tsCol][consec[0][0]] = newTS #re-name TimeSync call

					except IndexError:
						pass

					consec = [] #reset
		prevRow = row

	eventsData = np.delete(eventsArray, rowsToDelete)
	print " ", len(rowsToDelete), "rows deleted;", eventsData.size, "total events found."

	return eventsData



def addHeader(csvFile, MR):
	fd = open(csvFile,'a')
	fd.write("\n" + os.path.basename(__file__))
	fd.write("\n" + datetime.datetime.now().strftime("%I:%M%p %B %d %Y"))
	fd.write("\n" + "Model Region: " + MR)
	fd.close()
	
def defineBinsFromBounds(allbins, bounds):

	bins = []
	bound_nums = []
	for ind,i in enumerate(allbins):
	
		if ((i >= bounds[0]) and (i <= bounds[1])):
			bound_nums.append(i)
			
		if len(bound_nums) == 2:
			#ints = [bound_nums[0].is_integer(), bound_nums[1].is_integer()]
			#bounds = [int(b) if t else b for b,t in zip(bound_nums,ints)]
				
			bins.append(str(bound_nums[0]) + "_" + str(bound_nums[1]))
			bound_nums = [bound_nums[1]] #reset
			
	return bins
	

def main(parameter_file_path):

	parameters = getTxt(parameter_file_path)

	#read input summary data
	inputData = csvToArray(parameters['inputcsv'])
	
	#define LandTrendr bin groupings
	lt_disturbances = defineBinsFromBounds(parameters['lt_bins'], 
	parameters['lt_disturbance_bounds'])
	
	lt_nondisturbances = defineBinsFromBounds(parameters['lt_bins'], 
	parameters['lt_nondisturbance_bounds'])
	
	#define match dictionary
	matches = {}
	for i in lt_disturbances + parameters['ts_disturbances']: 
		matches[i] = "DISTURBANCE"
	for i in lt_nondisturbances + parameters['ts_nondisturbances']: 
		matches[i] = "NON_DISTURBANCE"
				
	#bin Timesync & LandTrendr data & apply tolerance if tolerance param > 0
	if "vertvals" in parameters['inputcsv']:
		binnedData = binValidationData(inputData, parameters['ltcolumn'], 
		parameters['lt_bins'], matches, yearCol="YEAR")
	else:
		binnedData = binValidationData(inputData, parameters['ltcolumn'], 
		parameters['lt_bins'], matches)
		
	arrayToCsv(binnedData, parameters['outputpath_events'])

# 	if parameters['tolerance'] > 0:
# 		if "vertvals" in parameters['inputcsv']:
# 			binnedData = applyYearTolerance(binnedData, parameters['tolerance'], matches, 
# 			lt_nondisturbances, yearCol="YEAR")
# 		else:
# 			binnedData = applyYearTolerance(binnedData, parameters['tolerance'], matches,
# 			lt_nondisturbances)
# 			
# 	arrayToCsv(binnedData, parameters['outputpath_yearlybins'])
# 	addHeader(parameters['outputpath_yearlybins'], parameters['modelregion'])
# 
# 	#isolate events
# 	if "vertvals" in parameters['inputcsv']:
# 		eventsData = isolateEvents(binnedData, yearCol="YEAR")
# 	else:
# 		eventsData = isolateEvents(binnedData)
# 	arrayToCsv(eventsData, parameters['outputpath_events'])
# 	addHeader(parameters['outputpath_events'], parameters['modelregion'])
# 
# 	#create broad confusion matrix
# 	labels = np.unique(eventsData["TS_MATCH"])
# 	inds = np.where(eventsData["TIMESYNC"] != "None")
# 	broadcm = makeConfusion(eventsData["TS_MATCH"][inds], eventsData["LT_MATCH"][inds], 
# 	labels)
# 	arrayToCsv(broadcm, parameters['outputpath_broadcm'])
# 	addHeader(parameters['outputpath_broadcm'], parameters['modelregion'])
# 
# 	detailedcm = makeConfusion_diffLabels(eventsData[inds], "TIMESYNC", "LANDTRENDR_FINAL")
# 	arrayToCsv(detailedcm, parameters['outputpath_detailedcm'])
# 	addHeader(parameters['outputpath_detailedcm'], parameters['modelregion'])


if __name__ == '__main__': 
	args = sys.argv
	if os.path.exists(args[1]):
		main(args[1])
	else:
		sys.exit('\nParameter File Not Found. Exiting.')