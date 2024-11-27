#conda activate myenv

echo "fill no data" 
gdal_fillnodata.py -md 20 -of GTiff ../tmp/dsm_raw.tif ../tmp/dsm.tif

echo "hillshading" 
gdaldem hillshade ../tmp/dsm.tif ../tmp/hillshade.tif -z 1 -s 1 -az 315 -alt 45

echo "slope"
gdaldem slope ../tmp/dsm.tif ../tmp/slope.tif -s 1

