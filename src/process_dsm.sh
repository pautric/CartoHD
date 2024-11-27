#conda activate myenv

echo "pipeline DSM" 
pdal pipeline p_dsm.json

gdal_fillnodata.py -md 20 -of GTiff dsm_raw.tif dsm.tif

echo "hillshading" 
gdaldem hillshade ../tmp/dsm.tif ../tmp/hillshade.tif -z 1 -s 1 -az 315 -alt 45

echo "slope"
gdaldem slope ../tmp/dsm.tif ../tmp/slope.tif -s 1

