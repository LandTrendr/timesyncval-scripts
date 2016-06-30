'''
difference.py

difference script
'''

from lthacks.lthacks import *

def main(inputCsv, fieldsToDifference, uidField, outputCsv):

	data = csvToArray(inputCsv)

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


	arrayToCsv(newdata, outputCsv)

if __name__ == '__main__': 

	args = sys.argv

	input_file = args[1]
	fields = [i.upper().strip() for i in args[2].split(",")]
	uid = args[3].upper().strip()
	output_file = args[4]

	sys.exit(main(input_file, fields, uid, output_file))