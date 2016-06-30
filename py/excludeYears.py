'''
Exclude Years.
Deletes rows from a summary table (aligned yearly LandTrendr & Timesync data) that 
corresponds data from to specific years. Outputs a new CSV.

Usage:
  excludeYears.py <inputcsv> <outputcsv> <startyear> <endyear> [--yearfield=<y>] [--meta=<m>]
  excludeYears.py -h | --help
    
Options:
  -h --help         Show this screen.
  --yearfield=<y>   Field name for year column in input csv. [default: YEAR]
  --meta=<m>        Additional description for metadata text file.
'''
import docopt, os, sys
import numpy as np
from lthacks.lthacks import *

def main(params):

    inputdata = csvToArray(params['<inputcsv>'])
    
    inputyears = list(np.unique(inputdata[params['--yearfield']]))
    
    outputyears = range(params['<startyear>'], params['<endyear>']+1)
    
    excludeyears = [i for i in inputyears if i not in outputyears]
    
    rows_to_del = []
    for ey in excludeyears:
        exrows = np.where(inputdata[params['--yearfield']] == ey)[0]
        rows_to_del.extend(exrows)

    outputdata = np.delete(inputdata, rows_to_del)
    
    #save output data
    arrayToCsv(outputdata, params['<outputcsv>'])
    this_script = os.path.abspath(__file__)
    createMetadata(sys.argv, params['<outputcsv>'], description=params['--meta'], 
    lastCommit=getLastCommit(this_script))
    

if __name__ == '__main__':

    try:
        #parse arguments, use file docstring as parameter definition
        args = docopt.docopt(__doc__)
        
        #format arguments
        for param in ['<startyear>', '<endyear>']:
            args[param] = int(args[param])

        args['--yearfield'] = args['--yearfield'].upper()
        
        #call main function
        sys.exit(main(args))
        
    #handle invalid options
    except docopt.DocoptExit as e:
        print e.message