from lthacks.lthacks import *

file = "conus_albers_3x3_extractions_allmetrics_difference_1986_2012.csv"

data = csvToArray(file)

pix_fields = ['VERTVALS_{0}'.format(str(i)) for i in range(1,10)]

rows_to_del = []

last_uid = None

uid_pixs = []
uid_rows = []

for r,row in enumerate(data):
	
	this_uid = row['UID']
	
	if this_uid != last_uid:
		if len(uid_pixs) > 0:
			if sum(uid_pixs) == 0:
				rows_to_del.extend(uid_rows)
	
		uid_pixs = [] #reset
		uid_rows = []
		
	uid_rows.append(r)
	for field in pix_fields: 
		uid_pixs.append(row[field])
		
		
	if row['CHANGE_PROCESS'] == '':
		rows_to_del.append(r)
		
newdata = np.delete(data, rows_to_del)

output_file = "conus_albers_3x3_extractions_allmetrics_difference_1986_2012_nozeros.csv"

arrayToCsv(newdata, output_file)
	
	
		
	