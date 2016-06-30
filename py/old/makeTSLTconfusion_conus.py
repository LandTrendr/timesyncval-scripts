import numpy as np
from lthacks.lthacks import *
import datetime

##DEFINITIONS OF TIMESYNC/LANDTRENDR CATEGORIES & MATCHES##
LT_BINS = [-1500, -250, -50, -10, -5, -0.001, 0.001, 5, 10, 50, 250, 1500] #dNBR
LT_DISTURBANCES = ["-1500_-250", "-250_-50", "-50_-10"]
LT_STABLE = ["-10_-5", "-5_-0.001", "-0.001_0.001", "0.001_5", "5_10"]
LT_NONDISTURBANCES = ["10_50", "50_250", "250_1500"]
TS_STABLE = ["STABLE", "OTHER NON-DISTURBANCE", "DELAY"]
TS_NONDISTURBANCES = ["RECOVERY"]
TS_DISTURBANCES = ["FIRE", "HARVEST", "MECHANICAL", "DEBRIS", "OTHER DISTURBANCE",
				   "SITE-PREPARATION FIRE", "STRESS", "WATER", "WIND"]
MATCH_DICT = {}
for i in LT_DISTURBANCES + TS_DISTURBANCES: MATCH_DICT[i] = "DISTURBANCE"
for i in LT_NONDISTURBANCES + TS_NONDISTURBANCES: MATCH_DICT[i] = "RECOVERY"
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
# 			elif title.lower() == "modelregion":
# 				MR = var
			elif title.lower() == 'tscolumn':
				tscolumn = var.upper()
			elif title.lower() == 'ltcolumn':
				ltcolumn = var.upper()	
			elif title.lower() == 'outputpath_yearlybins':
				outputpath_yearlybins = var		
			elif title.lower() == 'outputpath_broadcm':
				outputpath_broadcm = var
			elif title.lower() == 'outputpath_detailedcm':
				outputpath_detailedcm = var
	txt.close()
	return inputCsv, ltcolumn, tscolumn, outputpath_yearlybins, outputpath_broadcm, outputpath_detailedcm

def binValidationData(csvData, ltCol, tsCol, plotCol="PLOTID", yearCol="YEAR", ltbins=LT_BINS):
	'''Bins LandTrendr & Timesync data from aligned CSV data, outputs new data array'''
	
	print "\nBinning LandTrendr & TimeSync data..."
	#define new structured array & populate plot/year data
	dtypes = [(plotCol,'a32'), (yearCol,'f8'), ("TIMESYNC", 'a32'), ("LANDTRENDR", 'a32'), ("TS_MATCH", 'a32'), ("LT_MATCH", 'a32')]
	binnedArray = np.zeros(csvData.size, dtype=dtypes)
	binnedArray[plotCol] = csvData[plotCol]
	binnedArray[yearCol] = csvData[yearCol]

	#loop thru rows & bin data & populate "MATCH" columns w/ 'DISTURBANCE','NON-DISTURBANCE', or 'STABLE'
	#TimeSync binned by concatenating change process & relative magitude
	#LandTrendr binned using magnitude LT_BINS defined above
	digitized = np.digitize(csvData[ltCol], LT_BINS)
	for ind,row in enumerate(csvData):
		binnedArray["TIMESYNC"][ind] = str(row[tsCol].upper())
		binnedArray["LANDTRENDR"][ind] = str(LT_BINS[digitized[ind]-1]) + "_" + str(LT_BINS[digitized[ind]])
		
		try:
			binnedArray["TS_MATCH"][ind] = MATCH_DICT[binnedArray["TIMESYNC"][ind].upper()]
		except KeyError:
			binnedArray["TS_MATCH"][ind] = "BLANK"
		binnedArray["LT_MATCH"][ind] = MATCH_DICT[binnedArray["LANDTRENDR"][ind].upper()]
		
	print " Done binning."
	return binnedArray

# def addHeader(csvFile, MR):
# 	fd = open(csvFile,'a')
# 	fd.write("\n" + os.path.basename(__file__))
# 	fd.write("\n" + datetime.datetime.now().strftime("%I:%M%p %B %d %Y"))
# 	fd.write("\n" + "Model Region: " + MR)
# 	fd.close()

# def makeConfusion_detailed(data, truthCol, predictionCol):
#     '''Creates a confusion matrix for datasets w/ different truth & prediction labels. 
#     Does NOT calculate users/producers accuracy. truthCol/predictionCol are strings.'''
#     truthLabels = np.unique(data[truthCol]) 
#     predictionLabels = np.unique(data[predictionCol])
#     confusion = np.zeros((truthLabels.size+1, predictionLabels.size+1)).astype('str')
#     confusion[:,0] =  [""] + list(truthLabels)
#     confusion[0,:] =  [""] + list(predictionLabels)
# 
#     #populate confusion matrix
#     print confusion
#     for row in data:
#         x = np.where(confusion == row[truthCol])[0]
#         y = np.where(confusion == row[predictionCol])[1]
#         print row[truthCol]
#         print row[predictionCol]
#         print x,y
#         print confusion[x,y]
#         confusion[x,y] = str(float(confusion[x,y][0]) + 1)
# 
#     return confusion

def main(params):

	inputCsv, ltcolumn, tscolumn, outputpath_yearlybins, outputpath_broadcm, outputpath_detailedcm = getTxt(params)

	#bin TS & LT data & apply tolerance if > 0 - save columns
	inputData = csvToArray(inputCsv)
	binnedData = binValidationData(inputData, ltcolumn, tscolumn, plotCol="UID")
	arrayToCsv(binnedData, outputpath_yearlybins)
	#addHeader(outputpath_yearlybins, MR)
	print binnedData.size

	#create broad confusion matrix
	labels = np.unique(binnedData['LT_MATCH'])
	#inds = np.where( (binnedData["TIMESYNC"] != "BLANK") & (binnedData["TIMESYNC"] != ""))
	
	#do not compare all weirdos
	bad_inds = np.where( (binnedData["TIMESYNC"] == "BLANK") | (binnedData["TIMESYNC"] == ""))
	bad_uids = np.unique(binnedData['UID'][bad_inds])
	rows_to_del = []
	for uid in bad_uids:
		uid_ind = list(np.where(binnedData['UID'] == uid)[0])
		rows_to_del.extend(uid_ind)
	binnedData = np.delete(binnedData, rows_to_del)
	print binnedData.size
	
	broadcm = makeConfusion(binnedData["TS_MATCH"], binnedData["LT_MATCH"], labels)
	arrayToCsv(broadcm, outputpath_broadcm)
	#addHeader(outputpath_broadcm, MR)

	detailedcm = makeConfusion_diffLabels(binnedData, "TIMESYNC", "LANDTRENDR")
	arrayToCsv(detailedcm, outputpath_detailedcm)
	#addHeader(outputpath_detailedcm, MR)


if __name__ == '__main__': 
	args = sys.argv
	if os.path.exists(args[1]):
		main(args[1])
	else:
		sys.exit('\nParameter File Not Found. Exiting.')