
pdal pipeline p_veg.json
gdaldem color-relief "../tmp/vegetation.tif" -of GTiff -alpha color_table_vege.txt "../tmp/vegetation_color.tif"

pdal pipeline p_veg.json
gdaldem color-relief "../tmp/building.tif" -of GTiff -alpha color_table_bu.txt "../tmp/building_color.tif"
