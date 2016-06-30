'''
calcAccuracy_yearly.py

Generates accuracy tables using a year-by-year comparison between timesync & landtrendr data.

Parameters:
- inputcsv
- tscolumn
- ltcolumn
- ltbins
- ltdisturbance
- ltstable
- ltrecovery
- tsdisturbance
- tsstable
- tsrecovery
- outputpath_yearlybins
- outputpath_broadcm
- outputpath_detailedcm
- meta (opt.)
- plotcol (opt., default 'UID')
- yearcol (opt., default 'YEAR')

Output:
- yearly ts/lt bins CSV
- confusion matrix disturbance/stable/recov categories
- confusion matrix with individual lt & ts categories
'''

import numpy as np
from lthacks.lthacks import *
import datetime

def readParams(filePath):
	'''reads parameter file & extracts inputs'''

	txt = open(filePath, 'r')
	next(txt)

	params = {}

	for line in txt:
		if not line.startswith('#'):
			lineitems = line.split(':')
			title = lineitems[0].strip(' \n').lower()
			var = lineitems[1].strip(' \n')

			#format items
			if title in ["tscolumn", "ltcolumn", "plotcol", "yearcol"]:
				params[title] = var.upper()
				
			elif title == "ltbins":
				nums = [float(i) for i in var.split(",")]
				nums_formatted = [int(i) if i.is_integer() else i for i in nums] 
				params[title] = nums_formatted

			elif title in ["ltdisturbance", "ltstable", "ltrecovery", "tsdisturbance", "tsstable", "tsrecovery"]:
				params[title] = [i.strip().upper() for i in var.split(",")]

			else:
				params[title] = var

	txt.close()

	#fill in defaults
	if "meta" not in params:
		params['meta'] = ""
	if "plotcol" not in params:
		params['plotcol'] = "UID"
	if "yearcol" not in params:
		params['yearcol'] = "YEAR"
	
	#create lt/ts match dictionary	
	params['disturbances'] = params['ltdisturbance'] + params['tsdisturbance']
	params['stables'] = params['ltstable'] + params['tsstable']
	params['recoveries'] = params['ltrecovery'] + params['tsrecovery']
	
	params['matches'] = {}
	for i in params['disturbances']: params['matches'][i] = "DISTURBANCE"
	for i in params['stables']: params['matches'][i] = "STABLE"
	for i in params['recoveries']: params['matches'][i] = "RECOVERY"
	
	return params

def binValidationData(csvData, ltCol, tsCol, ltBins, matches, plotCol="PLOTID", yearCol="YEAR"):
	'''Bins LandTrendr & Timesync data from aligned CSV data, outputs new data array'''
	
	print "\nBinning LandTrendr & TimeSync data..."
	#define new structured array & populate plot/year data
	dtypes = [(plotCol,'a32'), (yearCol,'f8'), ("TIMESYNC", 'a32'), ("LANDTRENDR", 'a32'), ("TS_MATCH", 'a32'), ("LT_MATCH", 'a32')]
	binnedArray = np.zeros(csvData.size, dtype=dtypes)
	binnedArray[plotCol] = csvData[plotCol]
	binnedArray[yearCol] = csvData[yearCol]

	#loop thru rows & bin data & populate "MATCH" columns w/ 'DISTURBANCE','NON-DISTURBANCE', or 'STABLE'
	#TimeSync binned by concatenating change process & relative magitude
	#LandTrendr binned using magnitude ltBins defined above
	digitized = np.digitize(csvData[ltCol], ltBins)
	
	for ind,row in enumerate(csvData):
		binnedArray["TIMESYNC"][ind] = str(row[tsCol].upper())
		binnedArray["LANDTRENDR"][ind] = str(ltBins[digitized[ind]-1]) + "_" + str(ltBins[digitized[ind]])
		
		try:
			binnedArray["TS_MATCH"][ind] = matches[binnedArray["TIMESYNC"][ind].upper()]
		except KeyError:
			binnedArray["TS_MATCH"][ind] = "BLANK"
			
		binnedArray["LT_MATCH"][ind] = matches[binnedArray["LANDTRENDR"][ind].upper()]
		
	print " Done binning."
	return binnedArray


def main(params):
	
	metadesc = params['meta']
	thisfile = os.abspath(__file__)
	
	#bin TS & LT data - save columns
	inputData = csvToArray(params['inputcsv'])
	binnedData = binValidationData(inputData, params['ltcolumn'], params['tscolumn'], 
	params['ltbins'], params['matches'], plotCol=params['plotcol'], yearCol=params['yearcol'])
	arrayToCsv(binnedData, params['outputpath_yearlybins'])
	yearlybins_desc = " This file contains binned LandTrendr & Timesync data for all plots \
	and all years."
	createMetadata(sys.argv, params['outputpath_yearlybins'], description=metadesc+yearlybins_desc,
	lastCommit=getLastCommit(thisfile))
	
	#create broad confusion matrix
	labels = np.unique(binnedData['LT_MATCH'])
	broadcm = makeConfusion(binnedData["TS_MATCH"], binnedData["LT_MATCH"], labels)
	arrayToCsv(broadcm, params['outputpath_broadcm'])
	broadcm_desc = " This file contains LandTrendr vs. Timesync confusion matrix using\
	 using broad categories of DISTURBANCE, RECOVERY, & STABLE."
	createMetadata(sys.argv, params['outputpath_broadcm'], description=metadesc+broadcm_desc,
	lastCommit=getLastCommit(thisfile))

	#create detailed confusion matrix
	detailedcm = makeConfusion_diffLabels(binnedData, "TIMESYNC", "LANDTRENDR")
	arrayToCsv(detailedcm, params['outputpath_detailedcm'])
	detailedcm_desc = " This file contains LandTrendr vs. Timesync confusion matrix using\
	 using detailed categories LandTrendr bins vs. Timesync change process calls."
	createMetadata(sys.argv, params['outputpath_detailedcm'], description=metadesc+detailedcm_desc,
	lastCommit=getLastCommit(thisfile))


if __name__ == '__main__': 
	
	args = sys.argv
	paramfile = args[1]
	
	if os.path.exists(paramfile):
	
		params = readParams(paramfile)
		sys.exit(main(params))
		
	else:
	
		sys.exit('\nParameter File Not Found. Exiting.')