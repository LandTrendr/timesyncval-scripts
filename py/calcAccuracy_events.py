'''
calcAccuracy_events.py

Calculates producer's accuracy using an event-by-event comparison between timesync & landtrendr data.
Does not include stress, a long disturbance.

Parameters:
- yearlybins_csv
- output_csv
- tolerance

Output:
- CSV with list of timesync events
- CSV with producer's accuracy 
'''
import os, sys
import numpy as np
from lthacks.lthacks import *
		
def combineTsEvents(event_rows):

	#define list of dictionaries of combined ts events
	combined_events = []

	#initialize with 1st row in time series
	first_row = event_rows[0]
	uid = first_row['UID'] 
	prevYear = first_row['YEAR'] 
	prevName = first_row['TIMESYNC'] 
	dur = 1 
	firstYear = prevYear 

	dummy_row = np.array([(uid, 0, '', '', '', '')], dtype=event_rows.dtype)
	event_rows = np.append(event_rows, dummy_row, axis=0)
	
	for row in event_rows[1:]:
	
		thisYear = row['YEAR'] 
		thisName = row['TIMESYNC'] 
		
		#if consec to prev event...
		if (thisYear-prevYear) == 1: 
			
			firstYear = thisYear - dur 
			dur += 1 

			if (thisName != prevName): 
				thisName = prevName + "_" + thisName  
		
		#if not consec to prev event...			
		else: 
		
			eventName = prevName 
			
			event = {'UID': uid, 
					 'TS_YEAR': firstYear, 
					 'TS_BIN': eventName,
					 'TS_MATCH': 'DISTURBANCE',
					 'TS_DUR': dur} 
					 
			combined_events.append(event)
			
			dur = 1
			firstYear = thisYear 
				
		prevYear = thisYear 
		prevName = thisName 
		
	return combined_events #list of dictionaries


def main(yearlybins_csv, output_csv, tolerance):
	
	yearly_data = csvToArray(yearlybins_csv)
	
	event_cols = ['UID', 'TS_YEAR', 'TS_BIN', 'TS_MATCH', 'TS_DUR', 'LT_YEAR', 'LT_BIN', 'LT_MATCH'] 
	event_dtypes = ['a32', 'i8', 'a32', 'a32', 'i8', 'i8', 'a32', 'a32']
	event_data = np.zeros(yearly_data.size, dtype=zip(event_cols, event_dtypes))
	
	uids = np.unique(yearly_data['UID'])
	
	#fill in event_data with all timesync events
	event_row = 0
	for uid in uids:
		
		uid_rows = yearly_data[yearly_data['UID'] == uid] #uid rows
		
		tsevent_rows = uid_rows[ (uid_rows['TS_MATCH'] == 'DISTURBANCE') & 
		(uid_rows['TIMESYNC'] != 'STRESS') ] #uid fast event rows
		
		if len(tsevent_rows) > 0:
			ts_combined_events = combineTsEvents(tsevent_rows) #combined event dictionaries
		
			for event in ts_combined_events:
				for field in event:
					event_data[field][event_row] = event[field]
				event_row += 1
				
	#clean up unused rows
	rows_to_del = range(event_row, yearly_data.size)
	event_data = np.delete(event_data, rows_to_del)
	
	
	#find matching LandTrendr events
	num_events = event_data.size
	for r,row in enumerate(event_data):
	
		print "Event {0} of {1}".format(r+1, num_events)
	
		uid = row['UID']
		ts_first_year = row['TS_YEAR']
		ts_dur = row['TS_DUR']
		ts_last_year = ts_first_year + ts_dur - 1
		
		search_years = range(ts_first_year - tolerance, ts_last_year + tolerance + 1)
		rel_years = [y-ts_first_year for y in search_years]
		rel_years_abs = [abs(i) for i in rel_years]
		search_years_sorted = [y for (a,y) in sorted(zip(rel_years_abs, search_years))]
		
		for y,year in enumerate(search_years_sorted):
		
			year_row = yearly_data[ (yearly_data['UID'] == uid) & (yearly_data['YEAR'] == year) ] 
			
			if y == 0:
				orig_row = year_row
			
			if year_row['LT_MATCH'] == 'DISTURBANCE':
			
				event_data['LT_YEAR'][r] = year
				event_data['LT_BIN'][r] = year_row['LANDTRENDR'][0]
				event_data['LT_MATCH'][r] = 'DISTURBANCE'
				
				break
			
			if y == len(search_years_sorted)-1:
				event_data['LT_YEAR'][r] = orig_row['YEAR']
				event_data['LT_BIN'][r] = orig_row['LANDTRENDR'][0]
				event_data['LT_MATCH'][r] = 'NON_DISTURBANCE'	
	
	#save events csv		
	arrayToCsv(event_data, output_csv) 
	thisfile = os.path.abspath(__file__)
	createMetadata(sys.argv, output_csv, lastCommit=getLastCommit(thisfile))
	
	#calculate producer's accuracy
	lt_caught = float((event_data['LT_MATCH'] == "DISTURBANCE").sum())
	ts_events = float((event_data['TS_MATCH'] == "DISTURBANCE").sum())
	producers_acc = lt_caught/ts_events
	
	acc_cols = ["NUM_LT_CAUGHT_DISTURBANCES", "NUM_TS_DISTURBANCES", "PRODUCERS_ACCURACY"] 
	acc_dtypes = ['f8', 'f8', 'f8']
	acc_data = np.zeros(1, dtype=zip(acc_cols, acc_dtypes))
	acc_data["NUM_LT_CAUGHT_DISTURBANCES"][0] = lt_caught
	acc_data["NUM_TS_DISTURBANCES"][0] = ts_events
	acc_data["PRODUCERS_ACCURACY"][0] = producers_acc
	
	#save producer's accuracy as a CSV
	acc_csv = output_csv.replace('.csv', '_producersacc.csv')
	arrayToCsv(acc_data, acc_csv)
	createMetadata(sys.argv, acc_csv, lastCommit=getLastCommit(thisfile))
	

	
if __name__ == '__main__': 

	args = sys.argv

	sys.exit(main(args[1], args[2], int(args[3])))
		
			
			
	