'''
mergeEvents.py

Merge timesync validation event data from multiple runs into one master CSV.

inputs:
- parameters file with title & path of event CSV

output:
-  merged event CSV
'''
from lthacks.lthacks import *
from numpy.lib.recfunctions import append_fields


def txtToDict_string(txtfile):

	txt = open(txtfile, 'r')

	dictionary = {}
	for line in txt:
		comps = line.split(":")
		dictionary[comps[0].strip()] = comps[1].strip()

	return dictionary

def main(csvDict, outputPath):
	
	#loop through indiv event CSVs
	
	count = 0
	
	for title, path in csvDict.iteritems():
		
		data = csvToArray(path)
		
		#append all run headers to data structure
		
		data = append_fields(data, [i.upper() for i in csvDict.keys()], 
			data=[np.zeros(data.size) for i in csvDict.keys()],
			dtypes=['a25' for i in csvDict.keys()])
		
		if count == 0:
			
			#initialize final data structure
			mergedData = data
			mergedData[title.upper()][:] = 1
			count += 1
			continue
			
		#loop through rows and compare 
		
		for indivRow in data:
		
			#define event
			
			alreadyIncluded = False
			plot = indivRow['PLOTID']
			try:	
				year = indivRow['YEAR']
			except ValueError:
				year = indivRow['IMAGE_YEAR']
	
		
			for mergedRowNum, mergedRow in enumerate(np.array(mergedData)):
			
				try: 
					if (int(mergedRow['PLOTID']) == int(plot)) and (int(mergedRow['YEAR']) == int(year)):
					
						alreadyIncluded = True
						break
						
				except ValueError:
					try:
						if (int(mergedRow['PLOTID']) == int(plot)) and (int(mergedRow['IMAGE_YEAR']) == int(year)):
					
							alreadyIncluded = True
							break
						
					except ValueError:
						pass
					
			if alreadyIncluded:
				
				try:
					mergedData[title.upper()][mergedRowNum] = indivRow['LANDTRENDR_TOLERANT']
				except ValueError:
					mergedData[title.upper()][mergedRowNum] = indivRow['LANDTRENDR_FINAL']
				
			else:
			
				totalRows = mergedData.size
				mergedData = np.append(mergedData, np.array(indivRow, dtype=mergedData.dtype))

				try:
					mergedData[title.upper()][totalRows] = indivRow['LANDTRENDR_TOLERANT']
				except ValueError:
					mergedData[title.upper()][totalRows] = indivRow['LANDTRENDR_FINAL']	
			
		count += 1
		
	arrayToCsv(mergedData, outputPath)
	
	
if __name__ == '__main__': 

	args = sys.argv[1:]
	sys.exit(main(txtToDict_string(args[0]), args[1]))
	
	
	
	
	
				
			
			
			
			
		
		
		
		
		