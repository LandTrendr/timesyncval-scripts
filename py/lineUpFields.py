'''
lineUpFields.py
'''
from lthacks import *
from numpy.lib.recfunctions import append_fields

FIELDS_TO_ADD = ["X", "Y"]
DT = ["i8", "i8"]
IDFIELD = "PLOTID"

def main(inputCsv, addCsv, outputCsv, fieldsToAdd, dataTypes, uniqueField):
    
    #extract CSV data
    inputData = csvToArray(inputCsv)
    addData = csvToArray(addCsv)
    
    #add headers to input CSV
    headersToAdd = [field.upper() for field in fieldsToAdd]
    outputData = append_fields(inputData, headersToAdd, data=[np.zeros(inputData.size) for i in headersToAdd], dtypes=dataTypes)

    #loop thru input CSV rows
    for rownum, row in enumerate(inputData):

        uniqueID = row[uniqueField]

        for field in fieldsToAdd:

            fieldData = addData[field.upper()][addData[uniqueField] == uniqueID]
            outputData[field.upper()][rownum] = fieldData
            
    arrayToCsv(outputData, outputCsv)
    

if __name__ == '__main__': 
    args = sys.argv
    #print args
    sys.exit(main(args[1], args[2], args[3], FIELDS_TO_ADD, DT, IDFIELD))


