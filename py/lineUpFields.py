'''
lineUpFields.py

Adds column(s) to a CSV from field(s) of another CSV, 
lining up rows based on unique id field(s).

Parameters:
- input_csv
- add_csv
- output_csv
- fields_to_add 
- field_datatypes
- id_fields
- meta (opt.)

Output:
- CSV that is a copy of input_csv with added column(s) from add_csv
'''
from lthacks import *
from numpy.lib.recfunctions import append_fields

def readParams(paramfile):
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
            if title in ["fields_to_add", "id_fields"]:
                params[title] = [i.strip().upper() for i in var.split(",")]

            elif title == "field_datatypes":
                params[title] = [i.strip().lower() for i in var.split(",")]

            else:
                params[title] = var

    if 'meta' not in params:
        params['meta'] = None

    txt.close()

    return params

def main(inputCsv, addCsv, outputCsv, fieldsToAdd, dataTypes, uniqueFields, meta=None):

    #extract CSV data
    inputData = csvToArray(inputCsv)
    addData = csvToArray(addCsv)
    
    #add headers to input CSV
    headersToAdd = [field.upper() for field in fieldsToAdd]
    outputData = append_fields(inputData, headersToAdd, data=[np.zeros(inputData.size) for i in headersToAdd], 
        dtypes=dataTypes)

    #loop thru input CSV rows
    for rownum, row in enumerate(inputData):

        uniqueIDs = [row[f] for f in uniqueFields]

        for field in fieldsToAdd:

			try:
				#define where unique ids are located in addData
				bool_array = np.array([True]*addData.size)
				for g,f in enumerate(uniqueFields):
					bool_array = bool_array * (addData[f] == uniqueIDs[g])

				#get data from addData, and save in outputData
				fieldData = addData[field.upper()][bool_array][0]
				outputData[field.upper()][rownum] = fieldData
				
			except (IndexError, ValueError) as e:
				continue

    arrayToCsv(outputData, outputCsv)
    createMetadata(sys.argv, outputCsv, description=meta, lastCommit=getLastCommit(__file__)) 


if __name__ == '__main__': 
    
    paramfile = sys.argv[1]

    params = readParams(paramfile)

    sys.exit(main(params['input_csv'], params['add_csv'], params['output_csv'], 
        params['fields_to_add'], params['field_datatypes'], params['id_fields'], params['meta']))



