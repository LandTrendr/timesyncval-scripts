'''
extractVertvals.py

Extracts kernel from vertvals/vertyrs landtrendr maps & aligns with yearly timesync CSV,
creating a summary table ready for accuracy analysis. Timesync CSV must include start & 
end years of landtrendr run.

Parameters (in parameter file):
- tsplots (includes X, Y, UID, TSA)
- tssegments (includes UID, YEAR & CHANGE_PROCESS)
- scenesdir 
- searchstrings
- mapnames
- yearnames
- datanames
- scale (opt.)
- bands
- kernel
- metrics
- outputpath (.csv)
- xcol (default: 'X')
- ycol (default: 'Y')
- tsacol (default: 'TSA')
- uidcol (default: 'UID')
- yearcol (default: 'YEAR')
- meta (opt.)

Output:
- CSV file 
'''
from lthacks.lthacks import *
import numpy as np
import gdal, os, sys
import datetime
	
def ltmapKernelExtractor(plotData, scenesDir, ltmapSearchStrings, ltmapNames, bands, 
kernelSize, ltDataNames, scale=None, x_col="X", y_col="Y", tsa_col="TSA"):
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
					kernel = np.array(extract_kernel(ds, x, y, kernelSize, kernelSize, band, transform)).flatten()
					if scale and any(i in name for i in ltDataNames): # this was for Conus extractions where NBR was inverted
						kernel=kernel*scale
					
				except AttributeError: #kernel is out of bounds
					kernel = [-9999 for i in range(kernelSize**2)]
					
				bandHeaders = ["_".join([name, "BAND"+str(band), str(i)]) for i in pixels]
				
				for h,header in enumerate(bandHeaders): 
					plotData[header][r] = kernel[h]
				
	print "\n Done extracting kernels."
	return plotData	
   

def align_vertices(yearlyTSdata, ltYearNames, ltDataNames, ltKernelData, uid_col="UID", year_col="YEAR"):
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

			elif title == "scale":
				params[title] = float(var)

			elif title in ["xcol", "ycol", "tsacol", "uidcol", "yearcol"]:
				params[title] = var.upper()

			elif title in ["mapnames", "yearnames", "datanames"]:
				params[title] = [i.strip().upper() for i in var.split(",")]

			else:
				params[title] = var

	txt.close()

	if "meta" not in params:
		params['meta'] = None

	if "scale" not in params:
		params['scale'] = None

	return params
	
def run_extractions(tsPlotData, filename_template, params):
	
	ltData = ltmapKernelExtractor(tsPlotData, params['scenesdir'], params['searchstrings'],
	params['mapnames'], params['bands'], params['kernel'], params['datanames'], params['scale'], 
	params['xcol'], params['ycol'], params['tsacol'])
	
	
	#save lt extractions for safety
	now = datetime.datetime.now()
	outpath = filename_template.format(now.strftime("%m%d%Y%H%M"))
	arrayToCsv(ltData, outpath)
	
	return ltData
	
def run_alignment(tsSegData, ltData, filename_template, params):

	vertexData, valHeaders = align_vertices(tsSegData, params['yearnames'], params['datanames'], ltData, 
		params['uidcol'], params['yearcol'])
	
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
	print "\nCalculating summarize metrics..."
	
	summaryData = vertexData
	
	newFields = []
	for metric in params['metrics']:
		for prefix in params['datanames']:
			summaryData = appendMetric(summaryData, metric, prefix.upper())
			newField = metric.upper() + "_" + prefix.upper()
			newFields.append(newField)
			
	print "\tdone!"
	
	return summaryData, newFields
	
def calc_deltas(data, fieldsToDifference, uidField="UID"):
	print "\nCalculating delta values for metrics..."

	fieldsToAdd = ["D_"+f for f in fieldsToDifference]
	fieldPairs = zip(fieldsToAdd, fieldsToDifference)

	newdata = append_fields(data, fieldsToAdd, data=[np.zeros(data.size) for f in fieldsToAdd], dtypes=['f8'])

	last_uid = None
	for r,row in enumerate(newdata):

		this_uid = row[uidField]

		if this_uid != last_uid:
			last_uid = this_uid
			continue

		else:

			for d,f in fieldPairs:

				newdata[d][r] = row[f] - newdata[f][r-1]

			last_uid = this_uid
			
	print "\tdone!"
			
	return newdata


def main(paramfile):

	#extract parameters
	params = readParams(paramfile)
	
	#read timesync plots
	tsPlotData = csvToArray(params['tsplots'])

	#read yearly timesync segment csv
	tsSegData = csvToArray(params['tssegments'])
	
	#define output directory 
	outdir = os.path.dirname(params['outputpath'])
	
	rerun_all = False #saving steps as we go along, prompted by user to re-run

	#loop thru timesync plots & append landtrendr pixel extractions
	extract_outpath_template = params['outputpath'].replace('.csv', '_ltextraction_save_{0}.csv')
	save_files = glob.glob(extract_outpath_template.format("*"))
	
	if len(save_files) == 0:
	
		ltData = run_extractions(tsPlotData, extract_outpath_template, params)
		
	else:
		
		redo_bool = raw_input("\nLT extractions found: {0}, would you like to re-run extractions?(Y/N)".format(save_files))

		if "y" in redo_bool.lower():
			ltData = run_extractions(tsPlotData, extract_outpath_template, params)
			rerun_all = True
		else:
			print "\n\tusing most recent extractions from: ", save_files[-1]
			ltData = csvToArray(save_files[-1])
			

	#attach landtrendr vertex extractions to yearly timesync csv data
	align_outpath_template = params['outputpath'].replace('.csv', '_yearlyaligned_save_{0}.csv')
	save_files = glob.glob(align_outpath_template.format("*"))
	
	if (len(save_files) == 0) or rerun_all:
	
		vertexData, valHeaders = run_alignment(tsSegData, ltData, align_outpath_template, params)
		
	else:
	
		redo_bool = raw_input("\nAligned data found: {0}, would you like to re-run alignment?(Y/N)".format(save_files))
		
		if "y" in redo_bool.lower():
			vertexData, valHeaders = run_alignment(tsSegData, ltData, align_outpath_template, params)
			rerun_all=True
		else:
			print "\n\tusing most recent alignment data from: ", save_files[-1]
			vertexData = csvToArray(save_files[-1])
			valHeaders = filter(lambda x: any(x.startswith(i) for i in params['datanames']), vertexData.dtype.names)
			
	
	#interpolate between vertices	
	interp_outpath_template = params['outputpath'].replace('.csv', '_yearlyinterp_save_{0}.csv')
	save_files = glob.glob(interp_outpath_template.format("*"))
	
	if (len(save_files) == 0) or rerun_all:
	
		interpData = run_interpolation(vertexData, valHeaders, interp_outpath_template, params)
		
	else:
	
		redo_bool = raw_input("\nInterpolated data found: {0}, would you like to re-run interpolation?(Y/N)".format(save_files))
		
		if "y" in redo_bool.lower():
			interpData = run_interpolation(vertexData, valHeaders, interp_outpath_template, params)
		else:
			print "\n\tusing most recent interpolated data from: ", save_files[-1]
			interpData = csvToArray(save_files[-1])
		
	#calculate yearly LandTrendr summary metrics from kernels
	summaryData, newFields = calc_metrics(interpData, params)
	
	#difference the new fields
	deltaData = calc_deltas(summaryData, newFields, params['uidcol'])
	
	#save summary data
	arrayToCsv(deltaData, params['outputpath'])

	fullpath = os.path.abspath(__file__)
	createMetadata(sys.argv, params['outputpath'], description=params['meta'], lastCommit=getLastCommit(fullpath))

	
if __name__ == '__main__': 
	args = sys.argv
	sys.exit(main(args[1]))