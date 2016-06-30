'''
Downloads Yang's conus earth engine LandTrendr outputs
'''

import ee
import ee.mapclient
import urllib
import os, sys
import gdal
#sys.path.append('/usr/local/lib/python')
#from lthacks.lthacks import *

os.environ['GDAL_DATA'] = "/home/server/pi/homes/tlarrue/.conda/envs/ee-python/share/gdal"
gdal.SetConfigOption('GDAL_DATA', "/home/server/pi/homes/tlarrue/.conda/envs/ee-python/share/gdal")


def sixDigitTSA(pathrow):
    """converts TSA to 6-digit string for searching directories"""
    # pass pathrow, first coerce to string if not already
    if type(pathrow) != str: pathrow = str(pathrow)
    # check length, and make TSA six digit
    # e.g. for 4529, --> 045029
    pathrow = pathrow.strip()
    if len(pathrow) < 4:
        sys.exit("Enter TSA with at least 4 digits")
    elif len(pathrow) == 4:
        pathrow = '0' + pathrow[:2] + '0' + pathrow[2:]
    elif len(pathrow) == 5:
        if pathrow[0] == '0':
            pathrow = pathrow[:3] + '0' + pathrow[3:]
        elif pathrow[2] == '0':
            pathrow = '0' + pathrow
        else:
            sys.exit("Provide TSA of form PPRR e.g. 4529")
    return pathrow

def make_tiles(orig_longs, orig_lats, num_vertical, num_horizontal):
		longs = sorted(orig_longs)
		lats = sorted (orig_lats)

		width = float(longs[1] - longs[0])/float(num_vertical)
		height = float(lats[1] - lats[0])/float(num_horizontal)

		new_longs = []
		for i in range(num_vertical+1):
			if i == 0:
				new_longs.append(longs[0])
			else:
				new_longs.append(new_longs[i-1] + width)

		new_lats = []
		for i in range(num_horizontal+1):
			if i == 0:
				new_lats.append(lats[0])
			else:
				new_lats.append(new_lats[i-1] + height)

		pairs = [] #list of lists
		for i in range(num_vertical):
			for j in range(num_horizontal):
				#1 pair = [left, right, down, up]
				pairs.append([new_longs[i], new_longs[i+1], new_lats[j], new_lats[j+1]])

		print "\nTotal number of tiles to download: ", len(pairs)

		return pairs

def main(ee_image_path, bandnames, output_dir, num_vertical_tiles=None, num_horizontal_tiles=None):

	# Initialize the Earth Engine object, using the authentication credentials.
	ee.Initialize()

	#get conus run data
	data = ee.Image(ee_image_path)

	#Define a region roughly covering the continental US to use as download boundary
# 	longs = (-125.25, -66.0)
# 	lats = (22.5, 49.0)
# 	continentalUS = ee.Geometry.Rectangle(-125.25, 22.5, -66.0, 49.0)

	#isolate bands
	bands = data.select(bandnames)

	#break up US region into tiles
# 	tiles = make_tiles(longs, lats, num_vertical_tiles, num_horizontal_tiles)
# 	num_tiles = len(tiles)

	#break up US region by TSA
	us_tsas = ee.FeatureCollection('ft:14IJ0S4ridWhXPrvRBG3kRSQY_q17Ou6zzWiucl-k')
	
	#list of US tsas to filter thru
	us_tsa_dir = "/vol/v1/general_files/datasets/spatial_data/us_contiguous_tsa_masks_nobuffer"
	files = filter(lambda x: x.endswith('bsq'), os.listdir(us_tsa_dir))
	tsa_list = [int(i.split('_')[-1].replace('.bsq','')) for i in files]
	
	num_tsas = len(tsa_list)
	
# 	for ind,tile in enumerate(tiles):
	for ind,tsa in enumerate(tsa_list):

# 		print "\nWorking on tile ", ind+1, " of ", num_tiles, "..."
		print "\nWorking on tile ", ind+1, " of ", num_tsas, "..."

		#define file name
		# output_filename = ee_image_path.split("/")[-1] + "_" + "_".join([str(i) for i in tile]) + ".zip"
		output_filename = sixDigitTSA(tsa) + "_" + ee_image_path.split("/")[-1] + "_albers.zip"
		outdir = os.path.join(output_dir, sixDigitTSA(tsa))
		#output_path = os.path.join(output_dir, output_filename)
		output_path = os.path.join(outdir, output_filename)

		if not os.path.exists(output_path):

			#get download url
# 			url = bands.getDownloadUrl({
# 				'scale': 30, 
# 				'crs': 'EPSG:5070', 
# 				'region': '[[{0}, {3}], [{0}, {2}], [{1}, {2}], [{1}, {3}]]'.format(*[str(i) for i in tile])
# 			})
# 			
			#filter to tsa
			filtered = us_tsas.filter(ee.Filter.eq('WRS_ALB__1', tsa))

			coords = filtered.first().geometry().getInfo().get('coordinates')

			url = bands.getDownloadUrl({
				'scale': 30, 
				'crs': 'EPSG:5070', 
				'region': coords
			})

			print "\nYour download path:\n"+url
			
			#make output directory if does not exist
# 			if not os.path.exists(output_dir):
			if not os.path.exists(outdir):
				os.makedirs(outdir)
			
			#download the zipfile to server
			print "\nDownloading url to " + output_path + " ...."
			zipfile = urllib.URLopener()
			zipfile.retrieve(url, output_path)

			print "\tDone!"

		else:
			print output_path + " already exists. Skipping this tile."


if __name__ == '__main__': 

	args = sys.argv
	band = args[1]
	dir = args[2]
	
	ee_image_path = 'users/yang/20160502/nbr' #albers projection
	if band.lower()== 'yod':
		bandnames = ['doy{0}'.format(str(i)) for i in range(1,8)]
	elif band.lower()== 'raw':
		bandnames = ['raw{0}'.format(str(i)) for i in range(1,8)]
	elif band.lower()== 'ftv':
		bandnames = ['ftv{0}'.format(str(i)) for i in range(1,8)]
	else:
		bandnames = [band]
	#num_vertical_tiles = 20
	#num_horizontal_tiles = 12
	#240 tiles for conus
	output_dir = "/vol/v1/ee_conus/nbr/" + dir

	sys.exit(main(ee_image_path, bandnames, output_dir))


