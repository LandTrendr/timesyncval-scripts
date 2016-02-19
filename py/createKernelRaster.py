'''
createKernelRaster.py

turns kernels to plotID's => mask
'''

from lthacks import *
from intersectMask import *
import gdal, os, sys
from gdalconst import *
import numpy as np

def main(extentRaster, pointCsv, idfield, xfield, yfield, width, height, outputPath):

    # extract extent raster dataset
    
    ds = gdal.Open(extentRaster, GA_ReadOnly)
    band = ds.GetRasterBand(1)
    bandarray = band.ReadAsArray()
    transform = ds.GetGeoTransform()
    print transform
    print "rows = " + str(ds.RasterYSize) + "; cols = " + str(ds.RasterXSize)
    driver = ds.GetDriver()
    projection = ds.GetProjection()

    # ensure every pixel is set to 0
    
    bandarray[:] = 0
    print "array shape = ", bandarray.shape
    
    # extract point dataset
    
    points = csvToArray(pointCsv)
    
    # loop through points
    
    for ind,pt in enumerate(points):
    
    	print "row = ", ind
        
        # calculate indices of extent raster array of each point coordinate
        x = int(pt[xfield])
        y = int(pt[yfield])
        xoffset = int(x - transform[0])/30 - width/2
        yoffset = int(y - transform[3])/-30 - height/2
        x_indices = np.arange(xoffset, xoffset+width)
        y_indices = np.arange(yoffset, yoffset+height)
        
        print "X,Y = ", x, y
        print "Offsets = ", xoffset, yoffset
        print "Indices = ", x_indices, y_indices
        #toto = raw_input("keep going?")
        
        # turn pixels to have value of id field
        try:
        	check1 = [xoff<0 for xoff in x_indices]
        	check2 = [yoff<0 for yoff in y_indices]
        	if sum(check1) + sum(check2) > 0:
        		raise IndexError
        	else:
        		bandarray[np.repeat(y_indices,3), np.tile(x_indices,3)] = int(pt[idfield])
        except IndexError:
            print("\nID: " + str(pt[idfield]) + " outsize of boundaries. Excluding this point.")
            continue
            
    # save mask raster
    saveArrayAsRaster(bandarray, transform, projection, driver, outputPath, GDT_Int16, nodata=0)
    

if __name__ == '__main__':  

    xfield = "X"
    yfield = "Y"
    idfield = "PLOTID"
    extentRaster = "/vol/v1/general_files/datasets/spatial_data/modelregions/mr224_extent_mask.bsq"
    pointCsv = "/vol/v1/proj/timesync_validation/cmon_ts_interpretation/mr224_plots.csv"
    width = 3
    height = 3
    outputPath = "/vol/v1/proj/timesync_validation/tara_mr224_outputs/visualization/mr224_tsplots_mask.bsq"
    
    sys.exit(main(extentRaster, pointCsv, idfield, xfield, yfield, width, height, outputPath))
        
        