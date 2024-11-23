pdal pipeline p.json

echo "hillshading" 
gdaldem hillshade ../tmp/dtm.tif ../tmp/hillshade.tif -z 1 -s 1 -az 315 -alt 45

echo "slope"
gdaldem slope ../tmp/dtm.tif ../tmp/slope.tif -s 1

