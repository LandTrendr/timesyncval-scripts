'''
TESTING
extract 3x3 kernel from vertvals/vertyrs landtrendr maps & align with yearly timesync CSV
timesync CSV must include start & end years of landtrendr run.
*made for conus downloads

parameters:
	- timesyncPlotsCsv (includes X, Y, UID, TSA)
	- scenesDir (ex: "/vol/v1/ee_conus/nbr/stacks" or "/vol/v1/scenes")
	- ltmapSearchStrings (ex: [*vertvals.bsq, *vertyrs.bsq] or [outputs/nbr/*vertvals, 
	outputs/nbr/*vertyrs.bsq])
	- ltmapNames (ex: [NBR_VERTVALS, NBR_VERTYRS])
	- bands (ex: [[1,2,3,4,5,6,7], [1,2,3,4,5,6,7]])
	- kernelSize (ex: 3)
	- timesyncSegCsv

'''
from lthacks.lthacks import *
import numpy as np
import gdal, os, sys
import datetime
	
def ltmapKernelExtractor(plotData, scenesDir, ltmapSearchStrings, ltmapNames, bands, 
kernelSize, ltDataNames, x_col="X", y_col="Y", tsa_col="TSA"):
	'''Extracts kernel from LandTrendr Maps & appends to data array that includes X,Y, 
	TSA & PLOTID info.'''
	
	# append headers for each band & kernel pixel
	pixels = range(1, (kernelSize**2)+1)
	names_rep = np.repeat(ltmapNames,len(pixels)*len(bands))
	bands_rep = np.repeat(["BAND"+str(i) for i in bands*len(ltmapNames)], len(pixels))
	pixels_rep = np.tile(pixels, len(ltmapNames)*len(bands)).astype('str')
	
	combos = zip(names_rep, bands_rep, pixels_rep)
	headers = ["_".join(c) for c in combos] #NAME_BAND{band}_{pixel}
	plotData = append_fields(plotData, headers, data=[np.zeros(plotData.size) for i in headers], 
	dtypes='i2')
	
	#loop thru plotData rows
	print "\nlooping through plots..."
	for r,row in enumerate(plotData):
		
		tsa = sixDigitTSA(row[tsa_col])
		x = float(row[x_col])
		y = float(row[y_col])
		
		#find & open landtrendr maps
		for name,string in zip(ltmapNames,ltmapSearchStrings):
		
			fullString = os.path.join(scenesDir, tsa, string)
			files = glob.glob(fullString)
			
			try:
				mapPath = files[0]
				if len(files) > 1:
					print "WARNING: more than 1 file found for search string '{0}': \
					{1}\nUsing 1st file found.".format(string, "\n-".join(files))
			
			except IndexError:
				sys.exit("No applicable files found for search string: " + fullString)
			
			print "Extracting kernels from: ", mapPath, "..."	
			ds = gdal.Open(mapPath)
			transform = ds.GetGeoTransform()
			
			for band in bands:
			
				try:
					kernel = extract_kernel(ds, x, y, kernelSize, kernelSize, band, transform).flatten()
					if any(i in name for i in ltDataNames): 
						kernel=kernel*-1
					
				except AttributeError: #kernel is out of bounds
					kernel = [-9999 for i in range(kernelSize**2)]
					
				bandHeaders = ["_".join([name, "BAND"+str(band), str(i)]) for i in pixels]
				
				for h,header in enumerate(bandHeaders): 
					plotData[header][r] = kernel[h]
				
	print "\n Done extracting kernels."
	return plotData	
   

def align_vertices(yearlyTSdata, ltYearNames, ltDataNames, ltKernelData, metrics, uid_col="UID", year_col="YEAR"):
	'''Aligns repeated TimeSync & extracted LandTrendr data by uid & year -- Vertyrs/Vertvals version'''

	print "\nAligning LandTrendr extractions & yearly TimeSync interpretations..."

	#define lt data column names
	ltYearCols = filter(lambda x: any(x.startswith(i) for i in ltYearNames), ltKernelData.dtype.names)
	ltDataCols = filter(lambda x: any(x.startswith(i) for i in ltDataNames), ltKernelData.dtype.names)

	#append LT headers to repeated Timesync Data
	valHeaders = np.unique([i.split("_")[0] + "_" + i.split("_")[2] for  i in ltDataCols])
	vertexData = append_fields(yearlyTSdata, valHeaders, data=[np.zeros(yearlyTSdata.size) for i in valHeaders], dtypes='i2')

	#loop thru rows in yearly data & place LandTrendr extractions in right places
	print "\nlooping through yearly data & placing LT vertices..."
	numrows = vertexData.size
	for r,row in enumerate(vertexData):

		if r%100==0: print "row {0} of {1}".format(str(r+1), str(numrows))

		uid = row[uid_col]
		year = row[year_col]

		#isolate row in ltKernelData
		ltRow = ltKernelData[ltKernelData[uid_col] == uid]

		#find matching year bands
		yearBands = filter(lambda x: ltRow[x]==year, ltYearCols) #ex:['VERTYRS_BAND1_1', 'VERTYRS_BAND1_3']

		if len(yearBands) > 0:
			kernels = [i.split("_")[-1] for i in yearBands] #ex:['1', '3']
			vertexHeaders = [i + "_" + j for i in ltDataNames for j in kernels] #ex:['VERTVALS_BAND1_1', 'VERTVALS_BAND1_3']
			ltHeaders = [i.replace(i.split("_")[0], j) for i in yearBands for j in ltDataNames] #ex:['VERTVALS_1', 'VERTVALS_3']
			
			#fill in landtrendr data
			for ltheader,tsheader in zip(ltHeaders, vertexHeaders):
				vertexData[tsheader][r] = ltRow[ltheader]

	print "\tdone!"
	
	return vertexData, valHeaders
	
def interp_values(vertexData, valHeaders, uid_col="UID", year_col="YEAR"):
	'''interpolates LandTrendr values between vertices'''
	
	#interpolate between vertices 
	print "\nInterpolating between vertices..."
	
	uids = np.unique(vertexData[uid_col])
	numids = uids.size
	
	for u,uid in enumerate(uids):
		
		if u%100==0: print "uid {0} of {1}".format(u+1, numids)
		
		for pixel in valHeaders:
		
			uid_data_inds = np.sort(np.where( (vertexData[uid_col] == uid) & (vertexData[pixel] != 0) )[0])

			for i,ind in enumerate(uid_data_inds):

				if i==0: 
					prev_ind = ind
					continue

				if ind-prev_ind != 1:

					prev_val = float(vertexData[pixel][prev_ind])
					this_val = float(vertexData[pixel][ind])
					prev_year = int(vertexData[year_col][prev_ind])
					this_year = int(vertexData[year_col][ind])

					slope = (this_val - prev_val) / (this_year - prev_year)
					intercept = this_val - (slope * this_year)

					yearsToFill = vertexData[year_col][prev_ind+1:ind]

					values = slope*yearsToFill + intercept

					vertexData[pixel][prev_ind+1:ind] = values

				prev_ind = ind

			
	print "\tdone!"
				
	return vertexData
	

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
			if title in ["searchstrings", "metrics"]:
				params[title] = [i.strip() for i in var.split(",")]

			elif title == "bands":
				params[title] = [int(i) for i in var.split(",")]

			elif title == "kernel":
				params[title] = int(var)

			elif title in ["xcol", "ycol", "tsacol", "uidcol", "yearcol"]:
				params[title] = var.upper()

			elif title in ["mapnames", "yearnames", "datanames"]:
				params[title] = [i.strip().upper() for i in var.split(",")]

			else:
				params[title] = var

	txt.close()

	return params
	
def run_extractions(tsPlotData, filename_template, params):

	
	ltData = ltmapKernelExtractor(tsPlotData, params['scenesdir'], params['searchstrings'],
	params['mapnames'], params['bands'], params['kernel'], params['datanames'], params['xcol'], 
	params['ycol'], params['tsacol'])
	
	
	#save lt extractions for safety
	now = datetime.datetime.now()
	outpath = filename_template.format(now.strftime("%m%d%Y%H%M"))
	arrayToCsv(ltData, outpath)
	
	return ltData
	
def run_alignment(tsSegData, ltData, filename_template, params):

	vertexData, valHeaders = align_vertices(tsSegData, params['yearnames'], params['datanames'], ltData, 
		params['metrics'], params['uidcol'], params['yearcol'])
	
	#save aligned outputs for safety
	now = datetime.datetime.now()	
	outpath = filename_template.format(now.strftime("%m%d%Y%H%M"))
	arrayToCsv(vertexData, outpath)

	return vertexData, valHeaders
	
def run_interpolation(vertexData, valHeaders, filename_template, params):

	interpData = interp_values(vertexData, valHeaders, params['uidcol'], params['yearcol'])
	
	#save interpolated outputs for safety
	now = datetime.datetime.now()	
	outpath = filename_template.format(now.strftime("%m%d%Y%H%M"))
	arrayToCsv(vertexData, outpath)
	
	return interpData
	
def calc_metrics(vertexData, params):
	print "\ncalculating summarize metrics..."
	
	for metric in params['metrics']:
		for prefix in params['datanames']:
			summaryData = appendMetric(vertexData, metric, prefix.upper())
			
	print "\tdone!"
	
	return summaryData


def main(paramfile):

	params = readParams(paramfile)
	
	#read timesync plots
	tsPlotData = csvToArray(params['tsplots'])

	#read yearly timesync segment csv
	tsSegData = csvToArray(params['tssegments'])
	
	#define output directory 
	outdir = os.path.dirname(params['outputpath'])
	
	#loop thru timesync plots & append landtrendr pixel extractions
	extract_outpath_template = params['outputpath'].replace('.csv', '_ltextraction_save_{0}.csv')
	save_files = glob.glob(extract_outpath_template.format("*"))
	
	if len(save_files) == 0:
	
		ltData = run_extractions(tsPlotData, extract_outpath_template, params)
		
	else:
		
		redo_bool = raw_input("LT extractions found: {0}, would you like to re-run extractions?(Y/N)".format(save_files))

		if "y" in redo_bool.lower():
			ltData = run_extractions(tsPlotData, extract_outpath_template, params)
		else:
			print "\nusing extraction from: ", save_files[-1]
			ltData = csvToArray(save_files[-1])
			

	#attach landtrendr vertex extractions to yearly timesync csv data
	align_outpath_template = params['outputpath'].replace('.csv', '_yearlyaligned_save_{0}.csv')
	save_files = glob.glob(align_outpath_template.format("*"))
	
	if len(save_files) == 0:
	
		vertexData, valHeaders = run_alignment(tsSegData, ltData, align_outpath_template, params)
		
	else:
	
		redo_bool = raw_input("Aligned data found: {0}, would you like to re-run alignment?(Y/N)".format(save_files))
		
		if "y" in redo_bool.lower():
			vertexData, valHeaders = run_alignment(tsSegData, ltData, align_outpath_template, params)
		else:
			print "\nusing alignment data from: ", save_files[-1]
			vertexData = csvToArray(save_files[-1])
			valHeaders = filter(lambda x: any(x.startswith(i) for i in params['datanames']), vertexData.dtype.names)
			
	
	#interpolate between vertices	
	interp_outpath_template = params['outputpath'].replace('.csv', '_yearlyinterp_save_{0}.csv')
	save_files = glob.glob(interp_outpath_template.format("*"))
	
	if len(save_files) == 0:
	
		interpData = run_interpolation(vertexData, valHeaders, interp_outpath_template, params)
		
	else:
	
		redo_bool = raw_input("Interpolated data found: {0}, would you like to re-run interpolation?(Y/N)".format(save_files))
		
		if "y" in redo_bool.lower():
			interpData = run_interpolation(vertexData, interp_outpath_template, params)
		else:
			print "\nusing interpolated data from: ", save_files[-1]
			interpData = csvToArray(save_files[-1])
		
	#calculate yearly LandTrendr summary metrics from kernels
	summaryData = calc_metrics(interpData, params)

	#save summary data
	arrayToCsv(summaryData, params['outputpath'])

	
if __name__ == '__main__': 
	args = sys.argv
	sys.exit(main(args[1]))




	
	

	