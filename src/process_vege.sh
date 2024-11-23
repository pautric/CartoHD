
pdal pipeline p_veg.json

gdaldem color-relief "../tmp/vegetation.tif" -of GTiff -alpha color_table_vege.txt "../tmp/vegetation_green.tif"
