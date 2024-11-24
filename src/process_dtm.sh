
echo "Generalise DTM 1m"
gdalwarp -tr 1 1 -r bilinear ../tmp/dtm.tif ../tmp/dtm_g1.tif
gdal_contour -a elevation -i 5 -f GPKG ../tmp/dtm_g1.tif ../tmp/contours_g1.gpkg

echo "Generalise DTM 5m"
gdalwarp -tr 5 5 -r bilinear ../tmp/dtm.tif ../tmp/dtm_g5.tif
gdal_contour -a elevation -i 5 -f GPKG ../tmp/dtm_g5.tif ../tmp/contours_g5.gpkg

echo "Generalise DTM 10m"
gdalwarp -tr 10 10 -r bilinear ../tmp/dtm.tif ../tmp/dtm_g10.tif
gdal_contour -a elevation -i 5 -f GPKG ../tmp/dtm_g10.tif ../tmp/contours_g10.gpkg

