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
from itertools import groupby
from operator import itemgetter

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
	
def applyYearTolerance(binnedData, numYears):

	print "Applying year tolerance..."
	
	addColumns = ["MATCH_BOOL", "AVAIL_BOOL", "REPLACED_BOOL", "LANDTRENDR_TOLERANT", 
	"LT_MATCH_TOLERANT", "MATCH_TOLERANT"]
	
	outputData = append_fields(binnedData, addColumns, 
	data=[np.zeros(binnedData.size) for i in addColumns], dtypes='a32')
	
	#populate MATCH_BOOL column - does Timesync & LandTrendr match?
	outputData['MATCH_BOOL'] = (outputData['TS_MATCH'] == outputData['LT_MATCH'])
	
	#initiate AVAIL_BOOL column
	# - if MATCH_BOOL is True AND TS_MATCH is "DISTURBANCE", AVAIL_BOOL is False
	outputData['AVAIL_BOOL'] = ~np.logical_and((outputData['MATCH_BOOL']=="True"), 
	(outputData['TS_MATCH']=="DISTURBANCE"))
	
	#populate REPLACED_BOOL column
	outputData['REPLACED_BOOL'][:] = False
	
	#find rows to which to apply tolerance
	nomatch_inds = np.where( (outputData['MATCH_BOOL'] != "True") & 
	(outputData['TS_MATCH'] == "DISTURBANCE") )[0]
	
	#loop through non-matching rows
	for ind in nomatch_inds:
		
		altYears = range(1,numYears+1) + [-1*i for i in range(1,numYears+1)] #ex:[-1,1]
		
		for alt in altYears:

			try:
				print outputData['AVAIL_BOOL'][ind+alt]
				if outputData['AVAIL_BOOL'][ind+alt] == "False": continue
				if outputData['PLOTID'][ind+alt] != outputData['PLOTID'][ind]: continue
				altLT = outputData['LT_MATCH'][ind+alt]
				
				#if a nearby landtrendr disturbance is found...
				if altLT == "DISTURBANCE": 
					
					#populate tolerant columns fields with nearby info
					outputData['LANDTRENDR_TOLERANT'][ind] = outputData['LANDTRENDR'][ind+alt]
					outputData['LT_MATCH_TOLERANT'][ind] = altLT 
					
					#lock in new match so it cannot be used anywhere else
					outputData['AVAIL_BOOL'][ind] = False
					outputData['REPLACED_BOOL'][ind] = True
					
					#see if a switch is appropriate
					if (outputData['LT_MATCH'][ind] == outputData['TS_MATCH'][ind+alt]):
						outputData['AVAIL_BOOL'][ind+alt] = False
						outputData['LANDTRENDR_TOLERANT'][ind+alt] = outputData['LANDTRENDR'][ind]
						outputData['LT_MATCH_TOLERANT'][ind+alt] = outputData['LT_MATCH'][ind]	
						outputData['REPLACED_BOOL'][ind+alt] = True
				
					break
		
			except IndexError:
				continue
				
				
	#fill in rest of fields
	noreplace_inds = np.where(outputData['REPLACED_BOOL'] == "False")
	outputData['LANDTRENDR_TOLERANT'][noreplace_inds] = outputData['LANDTRENDR'][noreplace_inds]
	outputData['LT_MATCH_TOLERANT'][noreplace_inds] = outputData['LT_MATCH'][noreplace_inds]
	outputData['MATCH_TOLERANT'] = (outputData['TS_MATCH'] == outputData['LT_MATCH_TOLERANT'])
		
	return outputData
	
def combineSet(disturbances, magnitudes):
	'''test if possible to combine TimeSync disturbance set into one event'''
	
	if ("STABLE" in disturbances) or ("RECOVERY" in disturbances):
		newTS = None
	elif all([disturbances[0] == i for i in disturbances]): 
		newTS = disturbances[0] + "_" + str(np.mean(magnitudes).astype('int'))
	elif all([((i=="HARVEST") or (i=="SITE-PREPARATION FIRE")) for i in disturbances]):
		newTS = "Harvest_Site-preparation Fire".upper()
	else:
		newTS = None

	return newTS
	
def isolateEvents(tolerantData):

	'''reduce to one row per TS or LT event'''
	
	print "\nIsolating events..."
	
	#determine year column
	col_ind = ["YEAR" in i for i in tolerantData.dtype.names].index(True)
	year_col = tolerantData.dtype.names[col_ind]
	
	#determine LT_MATCH column
	if "LT_MATCH_TOLERANT" in tolerantData.dtype.names:
		ltmatch_col = "LT_MATCH_TOLERANT"
	else:
		ltmatch_col = "LT_MATCH"
		
	#determine LANDTRENDR column
	if "LANDTRENDR_TOLERANT" in tolerantData.dtype.names:
		landtrendr_col = "LANDTRENDR_TOLERANT"
	else:
		landtrendr_col = "LANDTRENDR"
		
	#determine TIMESYNC & LANDTRENDR indeces
	timesync_ind = list(tolerantData.dtype.names).index("TIMESYNC")
	landtrendr_ind = list(tolerantData.dtype.names).index(landtrendr_col)
	
	#find rows where there is either a TS or LT event
	disturbance_rows = tolerantData[(tolerantData['TS_MATCH'] == "DISTURBANCE") | 
	(tolerantData[ltmatch_col] == "DISTURBANCE")]
	
	#find consecutive rows
	consec_disturbances = []
	for rind,row in groupby(enumerate(disturbance_rows), lambda (i,x): i-x[year_col]):
		consec_disturbances.append(map(itemgetter(1), row))  #lists of consecutive disturbances
		
	#create new data structure
	colnames = list(tolerantData.dtype.names) + ["COMBINED_BOOL"]
	dtypes = [(i,'a32') for i in colnames]
	outputData = np.zeros(disturbance_rows.size, dtype=dtypes)
	
	#loop thru consecutive rows and test if combinable
	output_ind = 0
	for gind,group in enumerate(consec_disturbances):
	
		print group
	
		#if only 1 disturbance in group, add to event output
		if len(group) == 1:
		
			for cind,col in enumerate(tolerantData.dtype.names):
					outputData[col][output_ind] = group[0][cind]
			outputData["COMBINED_BOOL"][output_ind] = False
			
			output_ind += 1
		
		#if more than 1 disturbance in group, test if they can be combined	
		else:
		
			#separate disturbances and magnitudes
			disturbances = []
			magnitudes = []
			for row in group:
				ts_type_list = row[timesync_ind].split("_")
				disturbances.append(ts_type_list[0])
				magnitudes.append(int(ts_type_list[1]))
			
			#test if combinable using timesync column
			newTS = combineSet(disturbances, magnitudes)
			print newTS
			
			toto = raw_input("pause")
			
			#if combinable, determine combined landtrendr magnitude bin 
			if newTS: 
			
				lt_mags = []
				for row in group:
					lt_mags.append(row[landtrendr_ind].split("_"))
					
				max_ind = [int(i[1]) for i in lt_mags].index(max([int(i[1]) for i in lt_mags]))
			
				#add combined row to outputData
				for cind,col in enumerate(tolerantData.dtype.names):
					if col == "TIMESYNC":
						outputData[col][output_ind] = newTS
					else:
						outputData[col][output_ind] = group[max_ind][cind]
				outputData["COMBINED_BOOL"][output_ind] = True
				
				output_ind += 1
				
			else:
				for row in group:
				
					for cind,col in enumerate(tolerantData.dtype.names):
						outputData[col][output_ind] = row[cind]
					outputData["COMBINED_BOOL"][output_ind] = False
					
					output_ind += 1
					
	return outputData
				
	
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
	
	#apply year tolerance - save tolerance CSV
	if parameters['tolerance'] > 0:
		tolerantData = applyYearTolerance(binnedData, parameters['tolerance'])
		ltmatch_col = "LT_MATCH_TOLERANT"
		landtrendr_col = "LANDTRENDR_TOLERANT"
	else:
		ltmatch_col = "LT_MATCH"
		landtrendr_col = "LANDTRENDR"
		
	tolOutpath = os.path.splitext(parameters['outputpath_events'])[0] + "_tolerancetesting.csv"
	arrayToCsv(tolerantData, tolOutpath)
	tolDesc = "Results from applying 1-year tolerance"
	createMetadata(sys.argv, tolOutpath, description=tolDesc, lastCommit=getLastCommit(__file__))
	
	#isolate events - output events CSV
	eventData = isolateEvents(tolerantData)
	
	eventOutpath = parameters['outputpath_events']
	eventDesc = "List of LandTrendr or Timesync disturbance events."
	arrayToCsv(eventData, eventOutpath)
	createMetadata(sys.argv, eventOutpath, description=eventDesc, lastCommit=getLastCommit(__file__))
	
	#create broad confusion matrix - save as CSV
	labels = list(np.unique(eventData["TS_MATCH"]))
	if "" in labels:
		toto = labels.pop(labels.index(""))
	inds = np.where(eventData["TIMESYNC"] != "")
	broadcm = makeConfusion(eventData["TS_MATCH"][inds], eventData[ltmatch_col][inds], labels)
	
	broadPath = parameters['outputpath_broadcm']
	arrayToCsv(broadcm, broadPath)
	broadDesc = "LandTrendr vs. Timesync confusion matrix"
	createMetadata(sys.argv, broadPath, lastCommit=getLastCommit(__file__))

	#create detailed confusion - save as CSV
	detailedcm = makeConfusion_diffLabels(eventData[inds], "TIMESYNC", landtrendr_col)
	
	detailPath = parameters['outputpath_detailedcm']
	arrayToCsv(detailedcm, detailPath)
	detailDesc = "Detailed version of LandTrendr vs. Timesync confusion matrix"
	createMetadata(sys.argv, detailPath, description=detailDesc, lastCommit=getLastCommit(__file__))


if __name__ == '__main__': 
	args = sys.argv
	if os.path.exists(args[1]):
		main(args[1])
	else:
		sys.exit('\nParameter File Not Found. Exiting.')