#conda activate myenv

echo "pipeline DSM" 
pdal pipeline p_dsm.json

echo "hillshading" 
gdaldem hillshade ../tmp/dsm.tif ../tmp/hillshade.tif -z 1 -s 1 -az 315 -alt 45

echo "slope"
gdaldem slope ../tmp/dsm.tif ../tmp/slope.tif -s 1

