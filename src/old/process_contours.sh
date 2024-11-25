
echo "Generalise DTM"

#use smoothing instead
gdalwarp -tr 1 1 -r bilinear ../tmp/dtm.tif ../tmp/dtm_g1.tif

echo "Make contours"
gdal_contour -a elevation -i 5 -f GPKG ../tmp/dtm_g1.tif ../tmp/contours_g1.gpkg

