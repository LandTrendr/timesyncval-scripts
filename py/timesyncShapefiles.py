'''
timesyncShapefiles.py

Creates shapefiles from a CSV of X, Y coords & kernel. 

Attributes: PLOTID, TSA, X, Y, YEAR, CHANGE_PROCESS, RELATIVE_MAGNITUDE
Type: Points
Source: timesync vertex table
'''

import osgeo.ogr as ogr
import osgeo.osr as osr

import numpy as np
from lthacks import *
import os, sys

#list of shapefile attributes (shpname, datatype, stringwidth, csvname)
#ATTRIBUTES = [('PLOTID', ogr.OFTInteger, None, 'PLOTID'),
#              ('TSA', ogr.OFTInteger, None, 'TSA'),
#              ('X', ogr.OFTInteger, None, 'X'),
#              ('Y', ogr.OFTInteger, None, 'Y'),
#              ('YEAR', ogr.OFTInteger, None, 'YEAR'),
#              ('PROCESS', ogr.OFTString, 20, 'CHANGE_PROCESS'),
#              ('MAGNITUDE', ogr.OFTInteger, None, 'RELATIVE_MAGNITUDE')]

NUMPY_TO_OGR = {'i': ogr.OFTInteger, 'S': ogr.OFTString}
DEFAULT_STRING_WIDTH = 24

if "GDAL_DATA" not in os.environ:
    os.environ["GDAL_DATA"] = r'/usr/lib/anaconda/share/gdal'

def main(inputCsv, outputShp):
    
    #read CSV data so we can access by filed name
    inputData = csvToArray(inputCsv)

    #set up shapefile driver
    driver = ogr.GetDriverByName('ESRI Shapefile')
    
    #create the data source
    ds = driver.CreateDataSource(outputShp)
    
    #create the spatial reference
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(5070)
    
    #create the layer
    layername = os.path.splitext(os.path.basename(outputShp))[0]
    layer = ds.CreateLayer(layername, srs,ogr.wkbPoint)
    
    # dataSource = driver.Open(outputShp,1)

    #add fields to layer
    for fieldname, fieldtype in inputData.dtype.descr:
        
        #convert numpy data type to OGR data type
        fieldtype_stripped = fieldtype.strip("<")
        fieldtype_stripped = fieldtype_stripped.strip(">")
        fieldtype_stripped = fieldtype_stripped.strip("|")
        first_char = fieldtype_stripped[0]
        ogrtype = NUMPY_TO_OGR[first_char]        
        
        #define each field
        if fieldname == "DOMINANT_LANDUSE_OVER50":
            continue
        else:
            fielddef= ogr.FieldDefn(fieldname[:10], ogrtype) #10-char limit in .shp files
            print fieldname[:10], ogrtype
        
            #specify width if data type is a string
            if ogrtype == ogr.OFTString:
                fielddef.SetWidth(DEFAULT_STRING_WIDTH)
            
            layer.CreateField(fielddef)
        
            #clean up on each round
            del fielddef
        
        
    #process the csv data and add the attributes and features to shapefile
    for row in inputData:
        #create the feature
        feature = ogr.Feature(layer.GetLayerDefn())
        #Set the attribution using the values from the csv data
        for fieldname in inputData.dtype.names:
            if fieldname == "DOMINANT_LANDUSE_OVER50":
                continue
            else:
                feature.SetField(fieldname[:10], row[fieldname])
            
        #create the WKT for the feature using Python string formatting
        wkt = "POINT(%f %f) % (float(row['X']) , float(row['Y']))"
        
        #create the point from the well known txt
        point = ogr.CreateGeometryFromWkt(wkt)
        
        #Set the feature geometry using the point
        feature.SetGeometry(point)
        #Create the feature in the layer (shapefile)
        layer.CreateFeature(feature)
        #Detroy the feature to free resources
        feature.Destroy()
        
    #Destroy the data source to free resources
    ds.Destroy()
    

if __name__ == '__main__': 
    #args = sys.argv
    #if len(args)==3 and os.path.exists(args[1]):
    #    main(args[1], args[2])
    
    inputCsv = "/vol/v1/proj/timesync_validation/cmon_ts_interpretation/mr224_vertex_plotinfo_nocommas.csv"
    outputShp = "/vol/v1/proj/timesync_validation/tara_mr224_outputs/visualization/mr224_timesync_plots.shp"
    kernel = 3 #3x3 square
    main(inputCsv, outputShp)

