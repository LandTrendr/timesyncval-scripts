'''
Get vertyrs/vertvals stacks from conus downloads.
'''

import gdal, os, sys, subprocess, glob


def main(topDir, bandGroup, outputDir):

	bandGroup = bandGroup.strip().lower()
	if bandGroup not in ['yod','ftv','raw']:
		sys.exit('band group not understood.')
	
	## stack tiles
	
	tsa_dirs = os.listdir(topDir) #/vol/v1/ee_conus/nbr/yod
	num_tsas = len(tsa_dirs)
	print "\n{0} total TSAs found.".format(str(num_tsas))

	failed_zips = []
	
	for ind,dir in enumerate(tsa_dirs):
		
		print "\nWorking on {0}. TSA {1} of {2}...".format(dir, str(ind+1), str(num_tsas))
		
		thisDir = os.path.join(topDir, dir)
		os.chdir(thisDir)

		#define stacked file name
		if bandGroup == 'yod':
			stackedFilename = "{0}_ee_vertyrs_albers.bsq"
		elif bandGroup == 'ftv':
			stackedFilename = "{0}_ee_vertvals_albers.bsq"
		elif bandGroup == 'raw':
			stackedFilename = "{0}_ee_rawvals_albers.bsq"
			
		stackedPath = os.path.join(outputDir, dir, stackedFilename.format(dir))
		
		if (len(glob.glob('./*.tif')) < 7) and (not os.path.exists(stackedPath)):
		
			#unzip file
			zipFile = glob.glob("./*albers.zip")[0]
			zipCmd = "unzip {0}".format(zipFile)
			
			print zipCmd
			r = subprocess.call(zipCmd, shell=True)

			if r!=0:
				failed_zips.append(dir)



		else:
		
			print "skipping unzipping, already expanded."
			
		
		layers = glob.glob("./*.tif")
			
		if not os.path.exists(stackedPath):
		
			
			if not os.path.exists(os.path.dirname(stackedPath)): os.mkdir(os.path.dirname(stackedPath))
			stackTemp = 'gdal_merge.py -o {0} -of ENVI -ot Int16 -separate --config GDAL_DATA "/usr/lib/anaconda/share/gdal" {1}'
			
			layers_order = [int(i.split('.')[-2][-1]) for i in layers]
			ordered = [x for (y,x) in sorted(zip(layers_order,layers))]
			
			stackCmd = stackTemp.format(stackedPath, " ".join(ordered))
			
			print stackCmd
			subprocess.call(stackCmd, shell=True)
			
		else:
		
			print "skipping stacking, already stacked."
			
			
		#clean up
		print "cleaning up..."
		if os.path.exists(stackedPath):
			for l in layers:
				os.remove(l)
				os.remove(l.replace('tif','tfw'))
		print "\tDone!"

	#print failed zips, prompt user to check
	if len(failed_zips) > 0:
		print "We failed to unzip the following zipfiles: ", ", ".join(failed_zips)
			
		
	
if __name__ == '__main__': 

	args = sys.argv

	sys.exit(main(args[1], args[2], args[3]))
		
	
	
	
	
	