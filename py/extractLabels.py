'''
extractLabels.py

Extracts kernel from change label landtrendr maps & aligns with yearly timesync CSV,
creating a summary table ready for accuracy analysis. Timesync CSV must include start & 
end years of landtrendr run.

Parameters (in parameter file):
- tsplots (includes X, Y, UID, TSA)
- tssegments (includes UID, YEAR & CHANGE_PROCESS)
- scenesdir 
- searchstrings (ie. outputs/nbr/nbr_lt_labels/*_greatest_fast_disturbance_mmu11_tight.bsq)
- mapnames
- scale (opt.)
- bands
- banddefs
- databand
- yearband
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

def ltmapKernelExtractor(plotData, scenesDir, mapname, searchstring, bands, banddefs, kernelSize, x_col="X", y_col="Y", tsa_col="TSA"):
    '''Extracts kernel from LandTrendr Label Maps & appends to data array that includes X,Y & TSA info.'''

    # append headers for each band & kernel pixel
    #bandDefs = [ltmapclass.bands[i] for i in bands] #YOD, MAG, DUR
    headerCombos = zip(range(1,(kernelSize**2)+1)*len(banddefs),np.array([[banddefs[i]]*kernelSize**2 for i in range(len(banddefs))]).flatten())
    headersToAdd = [mapname + "_" + str(i[1]) + "_" + str(i[0]) for i in headerCombos] 
    plotData = append_fields(plotData, headersToAdd, data=[np.zeros(plotData.size) for i in headersToAdd], dtypes='i8')

    #loop thru plotData rows
    print "\nlooping through plots..."
    tsa = None
    for r,row in enumerate(plotData):
    
    	tsa = sixDigitTSA(row[tsa_col])
		x = float(row[x_col])
		y = float(row[y_col])
		
		fullString = os.path.join(scenesDir, tsa, searchstring)
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
                
        for b,band in enumerate(bands):
			
				try:
					kernel = np.array(extract_kernel(ds, x, y, kernelSize, kernelSize, band, transform)).flatten()
					
				except AttributeError: #kernel is out of bounds
					kernel = [-9999 for i in range(kernelSize**2)]
					
				bandHeaders = ["_".join([mapname, banddefs[b], str(i)]) for i in pixels]
				
				for h,header in enumerate(headersToAdd): 
					plotData[header][r] = kernel[h]

    print "\n Done extracting kernels."
    return plotData

def align_vertices(yearlyTSdata, ltKernelData, yearband, databand, year_col="YEAR", uid_col="UID"):
    '''Aligns repeated TimeSync & extracted LandTrendr data by plotid & year -- Disturbance map version'''

    print "\nAligning LandTrendr extractions & yearly TimeSync interpretations..."

    #append headers to repeated TimeSync Data
    headersToAdd = list(filter(lambda x: databand.upper() in x, ltKernelData.dtype.names))
    dataColumnPrefixes = [i[:-2] for i in headersToAdd]
    dataTypes = ["i8" for i in headersToAdd]
    yearColumns = list(filter(lambda x: yearband.upper() in x, ltKernelData.dtype.names))
    vertexData = append_fields(yearlyTSdata, headersToAdd, data=[np.zeros(yearlyTSdata.size) for i in headersToAdd], dtypes=dataTypes)

    #loop thru rows in repeated TS data
    print "\nlooping through yearly data & placing LT vertices..."
    ts_rowsToDelete = []
    numrows = vertexData.size
    for r,row in enumerate(vertexData):
    
    	if r%100==0: print "row {0} of {1}".format(str(r+1), str(numrows))

		uid = row[uid_col]
		year = row[year_col]
		
		#isolate row in ltKernelData
		ltRow = ltKernelData[ltKernelData[uid_col] == uid]
    	
    	#find matching year bands
		for y in yearColumns:
			if row[year_col] == ltRow[y]:
				for d in dataColumnPrefixes:
					vertexData[d+"_"+y[-1]][r] = ltRow[d+"_"+y[-1]]

    print "\n Done aligning outputs."
    return vertexData, headersToAdd
	

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

			elif title in ["mapnames", "banddefs"]:
				params[title] = [i.strip().upper() for i in var.split(",")]

			else:
				params[title] = var

	txt.close()

	if "meta" not in params:
		params['meta'] = None

	return params
	
def run_extractions(tsPlotData, filename_template, params):
	
	for mapname,searchstring in zip(params['mapnames'], params['searchstrings']):
		tsPlotData = ltmapKernelExtractor(tsPlotData, params['scenesdir'], mapname, searchstring, 
		params['bands'], params['banddefs'], params['kernel'], x_col=params['xcol'], 
		y_col=params['ycol'], tsa_col=params['tsacol'])
	
	ltData = tsPlotData
	
	#save lt extractions for safety
	now = datetime.datetime.now()
	outpath = filename_template.format(now.strftime("%m%d%Y%H%M"))
	arrayToCsv(ltData, outpath)
	
	return ltData
	
def run_alignment(tsSegData, ltData, filename_template, params):

	vertexData, valHeaders = align_vertices(tsSegData, ltData, params['yearband'], 
	params['databand'], year_col=params['yearcol'], uid_col=params['uidcol'])
	
	#save aligned outputs for safety
	now = datetime.datetime.now()	
	outpath = filename_template.format(now.strftime("%m%d%Y%H%M"))
	arrayToCsv(vertexData, outpath)

	return vertexData, valHeaders
	
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
			
		
	#calculate yearly LandTrendr summary metrics from kernels
	summaryData, newFields = calc_metrics(vertexData, params)
	
	#save summary data
	arrayToCsv(summaryData, params['outputpath'])

	fullpath = os.path.abspath(__file__)
	createMetadata(sys.argv, params['outputpath'], description=params['meta'], lastCommit=getLastCommit(fullpath))

	
if __name__ == '__main__': 
	args = sys.argv
	sys.exit(main(args[1]))