'''
fillGaps.py
'''

from lthacks import *
from numpy.lib.recfunctions import append_fields
import numpy as np
from itertools import groupby
from operator import itemgetter

def main(inputCsv, outputCsv, startYear, endYear):
    
    
    
    #extract CSV data
    inputData = csvToArray(inputCsv)
    
    #add headers to input CSV
    outputData = append_fields(inputData, ['NBR_MEAN_FILLED'], data=[np.zeros(inputData.size)], dtypes=['f8'])
    
    #LOOP THRU IDS
    uids = inputData['UID']

	for uid in uids:
	
		nan_inds = np.where( (inputData['UID'] == uid) & (np.isnan(inputData['NBR_SCALED_MEAN'])) )[0]
		
		if nan_inds.size == 0:
			continue
		
		else:
		
			#loop thru consec sets of indices
			for k, g in groupby(enumerate(list(nan_inds)), lambda (i, x): i-x):
			
				consec_inds = map(itemgetter(1), g)
				
				
				
				
			
			
		

    #loop thru input CSV rows
    for rownum, row in enumerate(uidData):

        id = str(row["ID"])
        uid = id[:5] + "_" + str(int(id[5:]))
        uidData["UID"][rownum] = uid
        
    #save csv with uids 
    arrayToCsv(uidData,  uidOutput)
    
    
    #create CSV with just 1 NBR value per year
    
    uids = np.unique(uidData['UID'])
    years = range(startYear, endYear+1)
    
    headers = ["UID", "YEAR", "NBR_SCALED_MEAN"]
    dtypes = ["a32", "i8", "f8"]
    outputData = np.zeros(uids.size*len(years), dtype=zip(headers,dtypes))
    
    outputData["UID"] = np.repeat(uids, len(years))
    outputData["YEAR"] = np.tile(years, uids.size)
    
    #take average of NBR if > 1 in one year
    for rownum, row in enumerate(outputData):
    	
    	uid = row['UID']
    	year = row['YEAR']
    	
    	uid_inds = np.where( (uidData['UID'] == uid) & (uidData['YEAR'] == year) )
    	nbrs = uidData['NBR_SCALED'][uid_inds]
    	
    	mean_nbr = np.nanmean(nbrs)
    	
    	outputData['NBR_SCALED_MEAN'][rownum] = mean_nbr
    	
    arrayToCsv(outputData, outputCsv)
    	

if __name__ == '__main__': 
    args = sys.argv
    #print args
    sys.exit(main(args[1], args[2], int(args[3]), int(args[4])))
