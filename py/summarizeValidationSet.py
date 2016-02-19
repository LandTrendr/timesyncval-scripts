"""
LandTrendr Validation with TimeSync interpretations.
This script produces a big CSV w/ Aligned TimeSync interpretations & extracted LandTrendr kernels
w/ summary stats on the LT pixels.

Tara Larrue (tlarrue2991@gmail.com)
"""
from lthacks.lthacks import *
from lthacks.ltmaps import *
import numpy as np
from numpy.lib.recfunctions import append_fields
import gdal

def stretchTimesync(interpData, idColumn="PLOTID", yearColumn="IMAGE_YEAR", interpColumn="CHANGE_PROCESS", 
                           columnsToInclude=["DOMINANT_LANDUSE_OVER50", "TSA", "PATCH_SIZE", "RELATIVE_MAGNITUDE"]):
    '''Paints timesync interpretations backwards through all years 1984-2012. Returns a structured array.'''

    #determine index of year & interpretation column
    yearColumnIndex = interpData.dtype.names.index(yearColumn)
    interpColumnIndex = interpData.dtype.names.index(interpColumn)

    #make list of unique plot ids
    plotIds = np.unique(interpData[idColumn])
    print "\n", plotIds.size, "timesync plot ids found."

    #loop thru ids, identify vertex years
    print "\nStretching TimeSync years..."
    repeatList = [] #append to a list for each year (faster than numpy arrays for unknown amt of growth)
    for id in plotIds:
        vertexYears = np.unique(np.sort(interpData[yearColumn][np.where(interpData[idColumn] == id)])) #years of vertices for plotid

        #for each vertex year, stretch data between that year and the next year
        for ind, year in enumerate(vertexYears):
            #append current vertex year row - defaults to 1st interpretation if there are multiples
            origRowInd = np.where((interpData[yearColumn] == year) & (interpData[idColumn] == id))[0][0] 
            repeatList.append(list(interpData[origRowInd])) 

            #if at last vertex year (2012), go on to next plot
            try:
                nextRowInd = np.where((interpData[yearColumn] == vertexYears[ind+1]) & (interpData[idColumn] == id))[0][0]
                numYearsToRepeat = vertexYears[ind+1] - year 
            except IndexError: 
                continue

            #if first vertex year for current plot & no change process, assign change process from next vertex year
            if (ind==0) and (repeatList[-1][interpColumnIndex] == ""): 
                repeatList[-1][interpColumnIndex] = interpData[interpColumn][nextRowInd]

            #change year when appending repeat rows
            for n in range(1,numYearsToRepeat):
                repeatList.append(list(interpData[nextRowInd]))
                repeatList[-1][yearColumnIndex] = year + n 

    #populate structured array from list
    print "\nRestructuring stretched data..."
    repeatData = np.zeros(len(repeatList), dtype=interpData.dtype)
    repeatArray = np.asarray(repeatList)
    for ind,column in enumerate(repeatData.dtype.names): 
        repeatData[column] = repeatArray[:,ind]

    print "\n Done stretching timesync interpretations."
    return repeatData[[idColumn, yearColumn, interpColumn] + columnsToInclude].copy()

def ltmapKernelExtractor(plotData, ltmapclass, bandNumbers, kernelSize, x_col="X", y_col="Y", tsa_col="TSA"):
    '''Extracts kernel from LandTrendr Maps & appends to data array that includes X,Y & TSA info.'''

    # append headers for each band & kernel pixel
    bandDefs = [ltmapclass.bands[i] for i in bandNumbers]
    headerCombos = zip(range(1,(kernelSize**2)+1)*len(bandDefs),np.array([[bandDefs[i]]*kernelSize**2 for i in range(len(bandDefs))]).flatten())
    headersToAdd = [ltmapclass.nickname + "_" + str(i[1]) + "_" + str(i[0]) for i in headerCombos] 
    plotData = append_fields(plotData, headersToAdd, data=[np.zeros(plotData.size) for i in headersToAdd], dtypes=ltmapclass.numpy_dtype)

    #loop thru plotData rows
    tsa = None
    for r,row in enumerate(plotData):
        if row[tsa_col] != tsa: #to avoid re-opening same map
            tsa = row[tsa_col]
            ltfile = getLTFile(tsa, ltmapclass.searchstrings)
            ds = gdal.Open(ltfile)
            transform = ds.GetGeoTransform()
            print "\nExtracting kernels from:", ltfile, "..."

        for b,band_num in enumerate(bandNumbers):
            kernel = extract_kernel(ds, float(row[x_col]), float(row[y_col]), int(kernelSize), int(kernelSize), band_num, transform).flatten()
            bandHeaders = headersToAdd[b*kernelSize**2:(b+1)*kernelSize**2]
            for l,label in enumerate(bandHeaders):
                plotData[label][r] = kernel[l]

    print "\n Done extracting kernels."
    return plotData

def align_lt_and_timesync(repeatedTSData, extractedLTData, yearColumnPrefix, dataColumnPrefixes, tsYearColumn="IMAGE_YEAR", idColumnLT="PLOTID", idColumnTS="PLOTID", addXYdata=[]):
    '''Aligns repeated TimeSync & extracted LandTrendr data by plotid & year -- Disturbance map version'''

    print "\nAligning LandTrendr extractions & yearly TimeSync interpretations..."

    #append headers to repeated TimeSync Data
    headersToAdd = list(filter(lambda x: any(x.startswith(i.upper()) for i in dataColumnPrefixes), extractedLTData.dtype.names))
    if addXYdata: headersToAdd = addXYdata + headersToAdd 
    dataTypes = ["i8" for i in headersToAdd]
    yearColumns = list(filter(lambda x: x.startswith(yearColumnPrefix.upper()), extractedLTData.dtype.names))
    repeatedTSData = append_fields(repeatedTSData, headersToAdd, data=[np.zeros(repeatedTSData.size) for i in headersToAdd], dtypes=dataTypes)

    #loop thru rows in repeated TS data
    ts_rowsToDelete = []
    for ts_index,ts_row in enumerate(repeatedTSData):

        #find plotid from ts data in lt data
        lt_index = np.where(extractedLTData[idColumnLT] == ts_row[idColumnTS])

        if lt_index[0].size > 0:
            #add X & Y info if necessary
            if addXYdata:
                for i in addXYdata:
                    repeatedTSData[i][ts_index] = extractedLTData[i][lt_index]

            #if TS image year matches LT image year, populate data columns for all kernels
            for y in yearColumns:
                if ts_row[tsYearColumn] == extractedLTData[y][lt_index]:
                    for d in dataColumnPrefixes:
                        repeatedTSData[d+"_"+y[-1]][ts_index] = extractedLTData[d+"_"+y[-1]][lt_index]

        else:
            ts_rowsToDelete.append(ts_index)

    print "\nDeleting {0} TimeSync vertices without plot info...".format(str(len(ts_rowsToDelete)))
    alignedData = np.delete(repeatedTSData, ts_rowsToDelete)

    print "\n Done aligning outputs."
    return alignedData

def align_lt_and_timesync_vert(repeatedTSData, extractedLTData, kernelSize, tsYearColumn="IMAGE_YEAR", idColumnLT="PLOTID", idColumnTS="PLOTID", addXYdata=[]):
    '''Aligns repeated TimeSync & extracted LandTrendr data by plotid & year -- Vertyrs/Vertvals version'''

    print "\nAligning LandTrendr extractions & yearly TimeSync interpretations..."

    #append headers to repeated TimeSync Data
    dataColumns = list(filter(lambda x: x.startswith("NBR_VERTVALS_VAL"), extractedLTData.dtype.names)) 
    yearColumns = list(filter(lambda x: x.startswith("NBR_VERTYRS_YR"), extractedLTData.dtype.names)) 
    valHeaders = [ltlabelmap['nbr_vertvals'].nickname + "_VAL_" + str(i) for i in range(1,(kernelSize**2)+1)]
    headersToAdd = valHeaders
    if addXYdata: headersToAdd = addXYdata + headersToAdd 
    dataTypes = ["i8" for i in headersToAdd]
    repeatedTSData = append_fields(repeatedTSData, headersToAdd, data=[np.zeros(repeatedTSData.size) for i in headersToAdd], dtypes=dataTypes)

    #loop thru rows in repeated TS data
    ts_rowsToDelete = []
    for ts_index,ts_row in enumerate(repeatedTSData):

        #find plotid from ts data in lt data
        lt_index = np.where(extractedLTData[idColumnLT] == ts_row[idColumnTS])

        if lt_index[0].size > 0:
            #add X & Y info if necessary
            if addXYdata:
                for i in addXYdata:
                    repeatedTSData[i][ts_index] = extractedLTData[i][lt_index]

            for y in yearColumns:
                print "\tColumn: ", y

                if ts_row[tsYearColumn] == extractedLTData[y][lt_index]:
                    kernel = y.split("_")[-1]
                    vertex = y.split("_")[2].split("YR")[1]
                    tsDataCol = ltlabelmap['nbr_vertvals'].nickname + "_VAL_" + kernel
                    ltDataCol = ltlabelmap['nbr_vertvals'].nickname + "_VAL" + vertex + "_" + kernel
                    repeatedTSData[tsDataCol][ts_index] = extractedLTData[ltDataCol][lt_index]

        else:
            ts_rowsToDelete.append(ts_index)

    print "\nDeleting {0} TimeSync vertices without plot info...".format(str(len(ts_rowsToDelete)))
    alignedData = np.delete(repeatedTSData, ts_rowsToDelete)

    #interpolate between vertices
    plotids = np.unique(alignedData[idColumnTS])
    for iter,id in enumerate(plotids):
        plot_ind = np.where(alignedData[idColumnTS] == id)
        plot = alignedData[plot_ind]
        for pixel in valHeaders:
            vertices = plot[plot[pixel] != 0] #values
            vertices_ind = np.where(alignedData[pixel][plot_ind] != 0)
            vertices_years = alignedData[tsYearColumn][vertices_ind]
            intercept = vertices_years[0]
            for vertex_num, vertex in enumerate(vertices):
                if vertex_num == 0: continue
                vertex_num-1
                print vertices[vertex_num-1], vertices_years[vertex_num], vertices_years[vertex_num-1]
                slope = vertex[1] - vertices[vertex_num-1][1]/vertices_years[vertex_num] - vertices_years[vertex_num-1]
                startnum = vertices_ind[0][vertex_num-1]+1
                endnum = vertices_ind[0][vertex_num]
                print startnum,endnum
                inbetween_years = alignedData[tsYearColumn][startnum:endnum]
                #inbetween_years = alignedData[tsYearColumn][vertices_ind[0][vertex_num-1]+1:vertices_ind[0][vertex_num]]
                fillers = [(slope*x)+intercept for x in inbetween_years]
                alignedData[pixel][vertices_ind[0][vertex_num-1]+1:vertices_ind[0][vertex_num]] = fillers


    print "\n Done aligning outputs."
    return alignedData

def getTxt(file):
    '''reads parameter file & extracts inputs'''
    txt = open(file, 'r')
    next(txt)

    for line in txt:
        if not line.startswith('#'):
            lineitems = line.split(':')
            title = lineitems[0].strip(' \n')
            var = lineitems[1].strip(' \n')

            if title.lower() == 'ltmaps':
                lt_maps_list = var.split(',')
                lt_maps = [ltlabelmap[i.strip()] for i in lt_maps_list]
            elif title.lower() == 'bands':
                bands = [int(i) for i in var.split(',')]
            elif title.lower() == 'kernelsize':
                kernelSize = int(var)
            elif title.lower() == 'tsas':
                tsas = [i.strip() for i in var.split(',')]
            elif title.lower() == 'metrics':
                metrics = [i.strip() for i in var.split(',')]
            elif title.lower() == 'timesyncplotspath':
                ts_plots_filepath = var
            elif title.lower() == 'timesyncinterppath':
                ts_interp_filepath = var
            elif title.lower() == 'outputpath':
                output_filepath = var
    txt.close()
    return lt_maps, bands, kernelSize, tsas, ts_plots_filepath, ts_interp_filepath, output_filepath, metrics

def main(params):
    #unpack inputs
    lt_maps, bands, kernelSize, tsas, ts_plots_filepath, ts_interp_filepath, output_filepath, metrics = getTxt(params)

    #extract & save kernel info from LT label maps for each TS plot (for given TSAs)
    ltData = extractTSArows(csvToArray(ts_plots_filepath), tsas)
    for mapclass in lt_maps:
        ltData = ltmapKernelExtractor(ltData, mapclass, bands, kernelSize)

    #open timesync interpretation file & extract data, then stretch years
    tsData = extractTSArows(csvToArray(ts_interp_filepath), tsas)
    tsData = stretchTimesync(tsData)

    #align timesync & lt data 
    #disturbance map case
    if any("disturbance" in i.searchstrings for i in lt_maps): 
        for ind,mapclass in enumerate(lt_maps):
            if (ind==0): 
                alignedData = align_lt_and_timesync(tsData, ltData, mapclass.nickname+"_YOD", [mapclass.nickname+"_MAG"], addXYdata=["X","Y"])
            else:
                alignedData = align_lt_and_timesync(alignedData, ltData, mapclass.nickname+"_YOD", [mapclass.nickname+"_MAG"]) 

        magColumnPrefixes = [i.nickname+"_MAG" for i in lt_maps]
        metricData, sumColumnPrefix = appendSumKernels(alignedData, magColumnPrefixes) #sum disturbance maps
        metricColumnPrefixes = magColumnPrefixes + [sumColumnPrefix]
    #vertyrs/vertvals case
    else: 
        #metricData = align_lt_and_timesync_vert(tsData, ltData, kernelSize, addXYdata=["X","Y"])
        metricData = align_lt_and_timesync_vert(tsData, ltData, kernelSize)
        metricColumnPrefixes = ["NBR_VERTVALS_VAL"]


    #append all metrics & save big CSV w/ TS, LT data & all metrics
    for mag in metricColumnPrefixes:
        for m in metrics:
            metricData = appendMetric(metricData, m, mag)
    arrayToCsv(metricData, output_filepath)


if __name__ == '__main__': 
    #args = sys.argv
    #if os.path.exists(args[1]):
    #    main(args[1])
    #else:
    #    sys.exit('\nParameter File Not Found. Exiting.')
    paramfile = "/vol/v1/proj/timesync_validation/tara_scripts/params/jan_2016/test_params.txt"
    sys.exit(main(paramfile))
    