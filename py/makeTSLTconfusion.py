'''
LandTrendr Validation with TimeSync interpretations.
This script takes a CSV w/ Aligned TimeSync interpretations & extracted LandTrendr kernels 
w/ summary stats on the LT pixels and creates 2 confusion matrices comparing given LT summary stat w/ TS data.

Author: Tara Larrue (tlarrue2991@gmail.com)
'''
import numpy as np
from lthacks.lthacks import *
import datetime

#DEFINITIONS OF TIMESYNC/LANDTRENDR CATEGORIES & MATCHES##
# LT_BINS = [0, 1, 4, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 200]
# LT_NONDISTURBANCES = ["0_1", "1_4", "4_10"]
# LT_DISTURBANCES = ["10_20", "20_30", "30_40", "40_50", "50_60", "60_70", "70_80", "80_90", "90_100", "100_200"]
# TS_NONDISTURBANCES = ["STABLE_0", "DELAY_1", "DELAY_2", "DELAY_3", "OTHER NON-DISTURBANCE_0", "RECOVERY_0"]
# TS_DISTURBANCES = ["FIRE_1", "FIRE_2", "FIRE_3", "HARVEST_0", "HARVEST_1", "HARVEST_2", "HARVEST_3",
# 				   "MECHANICAL_0", "MECHANICAL_1", "MECHANICAL_2", "MECHANICAL_3", "OTHER DISTURBANCE_1",
# 				   "OTHER DISTURBANCE_2", "SITE-PREPARATION FIRE_0", "SITE-PREPARATION FIRE_1", "SITE-PREPARATION FIRE_2", 
# 				   "SITE-PREPARATION FIRE_3", "STRESS_0", "STRESS_1", "STRESS_2", "STRESS_3", "WATER_2"]
# MATCH_DICT = {}
# for i in LT_DISTURBANCES + TS_DISTURBANCES: MATCH_DICT[i] = "DISTURBANCE"
# for i in LT_NONDISTURBANCES + TS_NONDISTURBANCES: MATCH_DICT[i] = "NON_DISTURBANCE"
###########################################################

# DEFINITIONS OF TIMESYNC/LANDTRENDR CATEGORIES & MATCHES - VERTVALS##
LT_BINS = [-1500, -250, -50, -10, -5, -0.001, 0.001, 5, 10, 50, 250, 1500] #dNBR
LT_DISTURBANCES = ["-1500_-250", "-250_-50", "-50_-10"]
#LT_STABLE = ["-10_-5", "-5_-0.001", "-0.001_0.001", "0.001_5", "5_10"]
#LT_NONDISTURBANCES = ["10_50", "50_250", "250_1500"]
LT_NONDISTURBANCES = ["-10_-5", "-5_-0.001", "-0.001_0.001", "0.001_5", "5_10", "10_50", "50_250", "250_1500"]
#TS_STABLE = ["STABLE_0","OTHER NON-DISTURBANCE_0","DELAY_1", "DELAY_2", "DELAY_3"]
#TS_NONDISTURBANCES = ["RECOVERY_0"]
TS_NONDISTURBANCES = ["RECOVERY_0", "STABLE_0","OTHER NON-DISTURBANCE_0","DELAY_1", "DELAY_2", "DELAY_3"]
TS_DISTURBANCES = ["FIRE_1", "FIRE_2", "FIRE_3", "HARVEST_0", "HARVEST_1", "HARVEST_2", "HARVEST_3",
				   "MECHANICAL_0", "MECHANICAL_1", "MECHANICAL_2", "MECHANICAL_3", "OTHER DISTURBANCE_1",
				   "OTHER DISTURBANCE_2", "SITE-PREPARATION FIRE_0", "SITE-PREPARATION FIRE_1", "SITE-PREPARATION FIRE_2", 
				   "SITE-PREPARATION FIRE_3", "STRESS_0", "STRESS_1", "STRESS_2", "STRESS_3", "WATER_2"]
MATCH_DICT = {}
for i in LT_DISTURBANCES + TS_DISTURBANCES: MATCH_DICT[i] = "DISTURBANCE"
for i in LT_NONDISTURBANCES + TS_NONDISTURBANCES: MATCH_DICT[i] = "NON_DISTURBANCE"
#for i in LT_STABLE + TS_STABLE: MATCH_DICT[i] = "STABLE"
# ##########################################################

def getTxt(file):
	'''reads parameter file & extracts inputs'''
	txt = open(file, 'r')
	next(txt)

	for line in txt:
		if not line.startswith('#'):
			lineitems = line.split(':')
			title = lineitems[0].strip(' \n')
			var = lineitems[1].strip(' \n')

			if title.lower() == 'inputcsv':
				inputCsv = var
			elif title.lower() == "modelregion":
				MR = var
			elif title.lower() == 'ltcolumn':
				ltcolumn = var			
			elif title.lower() == 'tolerance':
				tolerance = int(var)
			elif title.lower() == 'outputpath_yearlybins':
				outputpath_yearlybins = var
			elif title.lower() == 'outputpath_events':
				outputpath_events = var
			elif title.lower() == 'outputpath_broadcm':
				outputpath_broadcm = var
			elif title.lower() == 'outputpath_detailedcm':
				outputpath_detailedcm = var
			elif title.lower() == 'lt_bins':
				lt_bins = [float(i.strip()) for i in var.split(",")]	
		
	txt.close()
	return inputCsv, MR, ltcolumn, tolerance, outputpath_yearlybins, outputpath_events, \
	outputpath_broadcm, outputpath_detailedcm

def binValidationData(csvData, ltCol, tsCols=["CHANGE_PROCESS", "RELATIVE_MAGNITUDE"], 
                      plotCol="PLOTID", yearCol="IMAGE_YEAR", ltbins=LT_BINS):
	'''Bins LandTrendr & Timesync data from aligned CSV data, outputs new data array'''
	print "\nBinning LandTrendr & TimeSync data..."
	#define new structured array & populate plot/year data
	dtypes = [(plotCol,'f8'), (yearCol,'f8'), ("TIMESYNC", 'a32'), ("LANDTRENDR", 'a32'), 
	          ("TS_MATCH", 'a32'), ("LT_MATCH", 'a32')]
	binnedArray = np.zeros(csvData.size, dtype=dtypes)
	binnedArray[plotCol] = csvData[plotCol]
	binnedArray[yearCol] = csvData[yearCol]

	#loop thru rows & bin data & populate "MATCH" columns w/ 'DISTURBANCE' or 'NON-DISTURBANCE'
	#TimeSync binned by concatenating change process & relative magitude
	#LandTrendr binned using magnitude LT_BINS defined above
	digitized = np.digitize(csvData[ltCol], LT_BINS)
	for ind,row in enumerate(csvData):
		binnedArray["TIMESYNC"][ind] = str(row[tsCols[0]].upper()) + "_" + str(row[tsCols[1]]) 
		binnedArray["LANDTRENDR"][ind] = str(LT_BINS[digitized[ind]-1]) + "_" + str(LT_BINS[digitized[ind]])

		try:
			binnedArray["TS_MATCH"][ind] = MATCH_DICT[binnedArray["TIMESYNC"][ind].upper()]
			binnedArray["LT_MATCH"][ind] = MATCH_DICT[binnedArray["LANDTRENDR"][ind].upper()]
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

def applyYearTolerance(binnedData, plotCol="PLOTID", yearCol="IMAGE_YEAR", yearTolerance=1): 
	'''Bins LandTrendr & Timesync data from aligned CSV data, then creates a '''
	print "\nApplying " + str(yearTolerance) + " year tolerance..."
	#define new structured array
	altYears = range(1,yearTolerance+1)
	ltAlts = ["LANDTRENDR_ALT{0}".format(k) for k in ["-"+str(i) for i in altYears]+["+"+str(j) for j in altYears]]
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
						binnedData["LT_MATCH"][ind] = MATCH_DICT[binnedData[alt][ind].upper()] 
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

		if (MATCH_DICT[binnedData["LANDTRENDR_FINAL"][ind]] == "DISTURBANCE"):
			if (MATCH_DICT[binnedData["LANDTRENDR_FINAL"][ind-1]] == "DISTURBANCE") and (binnedData["LANDTRENDR_FINAL"][ind-1] == binnedData["LANDTRENDR_FINAL"][ind]):
				
				for bin in LT_NONDISTURBANCES:
					edges = [float(b) for b in bin.split("_")]
					print edges
					if (0 >= edges[0]) and (0 <= edges[1]):
						lt_zero_bin = bin
						binnedData["LANDTRENDR_FINAL_NOCONSEC"][ind] = lt_zero_bin
						print "here", ind
						
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

def main(params):

	inputCsv, MR, ltcolumn, tolerance, outputpath_yearlybins, outputpath_events, \
	outputpath_broadcm, outputpath_detailedcm = getTxt(params)

	#bin TS & LT data & apply tolerance if > 0 - save columns
	inputData = csvToArray(inputCsv)

		
	if "vertvals" in inputCsv:
		binnedData = binValidationData(inputData, ltcolumn, yearCol="YEAR")
	else:
		binnedData = binValidationData(inputData, ltcolumn)
	
	if tolerance > 0:
		if "vertvals" in inputCsv:
			binnedData = applyYearTolerance(binnedData, yearCol="YEAR", yearTolerance=tolerance)
		else:
			binnedData = applyYearTolerance(binnedData, yearTolerance=tolerance)
			
	arrayToCsv(binnedData, outputpath_yearlybins)
	addHeader(outputpath_yearlybins, MR)

	#isolate events
	if "vertvals" in inputCsv:
		eventsData = isolateEvents(binnedData, yearCol="YEAR")
	else:
		eventsData = isolateEvents(binnedData)
	arrayToCsv(eventsData, outputpath_events)
	addHeader(outputpath_events, MR)

	#create broad confusion matrix
	labels = np.unique(eventsData["TS_MATCH"])
	inds = np.where(eventsData["TIMESYNC"] != "None")
	broadcm = makeConfusion(eventsData["TS_MATCH"][inds], eventsData["LT_MATCH"][inds], labels)
	arrayToCsv(broadcm, outputpath_broadcm)
	addHeader(outputpath_broadcm, MR)

	detailedcm = makeConfusion_diffLabels(eventsData[inds], "TIMESYNC", "LANDTRENDR_FINAL")
	arrayToCsv(detailedcm, outputpath_detailedcm)
	addHeader(outputpath_detailedcm, MR)


if __name__ == '__main__': 
	args = sys.argv
	if os.path.exists(args[1]):
		main(args[1])
	else:
		sys.exit('\nParameter File Not Found. Exiting.')