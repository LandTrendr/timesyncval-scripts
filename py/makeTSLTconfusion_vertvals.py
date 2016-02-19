import numpy as np
from lthacks.lthacks import *
import datetime

##DEFINITIONS OF TIMESYNC/LANDTRENDR CATEGORIES & MATCHES##
LT_BINS = [-1500, -250, -50, -5, -0.001, 0.001, 5, 50, 250, 1500] #dNBR
LT_DISTURBANCES = ["-1500_-250", "-250_-50", "-50_-5"]
LT_STABLE = ["-5_-0.001", "-0.001_0.001", "0.001_5"]
LT_NONDISTURBANCES = ["5_50", "50_250", "250_1500"]
TS_STABLE = ["STABLE_0","OTHER NON-DISTURBANCE_0","DELAY_1", "DELAY_2", "DELAY_3"]
TS_NONDISTURBANCES = ["RECOVERY_0"]
TS_DISTURBANCES = ["FIRE_1", "FIRE_2", "FIRE_3", "HARVEST_0", "HARVEST_1", "HARVEST_2", "HARVEST_3",
				   "MECHANICAL_0", "MECHANICAL_1", "MECHANICAL_2", "MECHANICAL_3", "OTHER DISTURBANCE_1",
				   "OTHER DISTURBANCE_2", "SITE-PREPARATION FIRE_0", "SITE-PREPARATION FIRE_1", "SITE-PREPARATION FIRE_2", 
				   "SITE-PREPARATION FIRE_3", "STRESS_0", "STRESS_1", "STRESS_2", "STRESS_3", "WATER_2"]
MATCH_DICT = {}
for i in LT_DISTURBANCES + TS_DISTURBANCES: MATCH_DICT[i] = "DISTURBANCE"
for i in LT_NONDISTURBANCES + TS_NONDISTURBANCES: MATCH_DICT[i] = "NON_DISTURBANCE"
for i in LT_STABLE + TS_STABLE: MATCH_DICT[i] = "STABLE"
############################################################

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
				ltcolumn = var.upper()	
			elif title.lower() == 'outputpath_yearlybins':
				outputpath_yearlybins = var		
			elif title.lower() == 'outputpath_broadcm':
				outputpath_broadcm = var
			elif title.lower() == 'outputpath_detailedcm':
				outputpath_detailedcm = var
	txt.close()
	return inputCsv, MR, ltcolumn, outputpath_yearlybins, outputpath_broadcm, outputpath_detailedcm

def binValidationData(csvData, ltCol, tsCols=["CHANGE_PROCESS", "RELATIVE_MAGNITUDE"], 
                      plotCol="PLOTID", yearCol="YEAR", ltbins=LT_BINS):
	'''Bins LandTrendr & Timesync data from aligned CSV data, outputs new data array'''
	print "\nBinning LandTrendr & TimeSync data..."
	#define new structured array & populate plot/year data
	dtypes = [(plotCol,'f8'), (yearCol,'f8'), ("TIMESYNC", 'a32'), ("LANDTRENDR", 'a32'), ("TS_MATCH", 'a32'), ("LT_MATCH", 'a32')]
	binnedArray = np.zeros(csvData.size, dtype=dtypes)
	binnedArray[plotCol] = csvData[plotCol]
	binnedArray[yearCol] = csvData[yearCol]

	#loop thru rows & bin data & populate "MATCH" columns w/ 'DISTURBANCE','NON-DISTURBANCE', or 'STABLE'
	#TimeSync binned by concatenating change process & relative magitude
	#LandTrendr binned using magnitude LT_BINS defined above
	digitized = np.digitize(csvData[ltCol], LT_BINS)
	for ind,row in enumerate(csvData):
		binnedArray["TIMESYNC"][ind] = str(row[tsCols[0]].upper()) + "_" + str(row[tsCols[1]]) 
		binnedArray["LANDTRENDR"][ind] = str(LT_BINS[digitized[ind]-1]) + "_" + str(LT_BINS[digitized[ind]])
		binnedArray["TS_MATCH"][ind] = MATCH_DICT[binnedArray["TIMESYNC"][ind].upper()]
		binnedArray["LT_MATCH"][ind] = MATCH_DICT[binnedArray["LANDTRENDR"][ind].upper()]

	print " Done binning."
	return binnedArray

def addHeader(csvFile, MR):
	fd = open(csvFile,'a')
	fd.write("\n" + os.path.basename(__file__))
	fd.write("\n" + datetime.datetime.now().strftime("%I:%M%p %B %d %Y"))
	fd.write("\n" + "Model Region: " + MR)
	fd.close()

def main(params):

	inputCsv, MR, ltcolumn, outputpath_yearlybins, outputpath_broadcm, outputpath_detailedcm = getTxt(params)

	#bin TS & LT data & apply tolerance if > 0 - save columns
	inputData = csvToArray(inputCsv)
	binnedData = binValidationData(inputData[inputData["CHANGE_PROCESS"] != "no_data"] , ltcolumn)
	arrayToCsv(binnedData, outputpath_yearlybins)
	addHeader(outputpath_yearlybins, MR)

	#create broad confusion matrix
	labels = np.unique(binnedData["TS_MATCH"])
	inds = np.where(binnedData["TIMESYNC"] != "None")
	broadcm = makeConfusion(binnedData["TS_MATCH"][inds], binnedData["LT_MATCH"][inds], labels)
	arrayToCsv(broadcm, outputpath_broadcm)
	addHeader(outputpath_broadcm, MR)

	detailedcm = makeConfusion_diffLabels(binnedData[inds], "TIMESYNC", "LANDTRENDR")
	arrayToCsv(detailedcm, outputpath_detailedcm)
	addHeader(outputpath_detailedcm, MR)


if __name__ == '__main__': 
	args = sys.argv
	if os.path.exists(args[1]):
		main(args[1])
	else:
		sys.exit('\nParameter File Not Found. Exiting.')