'''
Unzip earth engine downloads and reformat to standard LT format.
'''

import gdal, os, sys, subprocess, glob


def main(topDir, subDirs, numBands, outputDir):
	
	## stack tiles
	
	#get list of zipfiles
	firstDir = os.path.join(topDir,subDirs[0])
	zipFiles = filter(lambda x: x.endswith(".zip"), os.listdir(firstDir))
	print "\n{0} total tiles found.".format(str(len(zipFiles)))
	
	#unzip all files into indiv folders
	print "\nUnzipping files..."
	
	num_files = len(zipFiles)*len(subDirs)
	stacks = [] #accumulate list of files to stack
	for f,file in enumerate(zipFiles):
	
		stacks.append([])
		
		for d,dir in enumerate(subDirs):
		
			print "\nWorking on file {0} of {1}...".format(str((f+1)*(g+1)), str(num_files))
	
			dirPath = os.path.join(topDir, dir)
			filePath = os.path.join(dirPath, file)
			zipFolder = os.path.splitext(filePath)[0]
			unzippedFile = glob.glob(os.path.join(zipFolder,"*.tif"))[0]
			
			if not os.path.exists(unzippedFile):
			
				zipCmd = "unzip {0} -d {1}".format(filePath, zipFolder)
				print zipCmd
				subprocess.call(zipCmd, shell=True)
			
				mvCmd =  "mv {0} {1}".format(filePath, zipFolder)
				print mvCmd
				subprocess.call(mvCmd, shell=True)
			
				stacks[f].append(unzippedFile)
				
			else:
				
				print "skipping file {0}, already zipped.".format(filePath)
			
			
	#stack all files using gdal
	print "\nStacking all file groups..."
	
	num_stacks = len(stacks)
	for g,group in enumerate(stacks):
		
		print "\nWorking on stack {0} of {1}...".format(str(g+1), str(num_stacks))
		 
		outFilename = os.path.basename(group[0]).replace("zip", "bsq")
		outPath = os.path.join(outputDir, outFilename)
		
		if not os.path.exists(outPath):
			stackTemp = "gdal_merge.py -o {0} -of ENVI -ot Int16 -v -separate --config GDAL_DATA “/usr/lib/anaconda/share/gdal” {1}"
			stackCmd = stackTemp.format(outPath, " ".join(group))
		
			print stackCmd
			subprocess.call(stackCmd)
			
		else:
		
			print "{0} already exists. skipping this group.".format(outPath)
		
		
	
	
	
	
	