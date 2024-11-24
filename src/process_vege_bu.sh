
echo "pipeline veg bu"
pdal pipeline p_veg_bu.json

echo "color vege"
gdaldem color-relief "../tmp/vegetation.tif" -of GTiff -alpha color_table_vege.txt "../tmp/vegetation_color.tif"

echo "color bu"
gdaldem color-relief "../tmp/building.tif" -of GTiff -alpha color_table_bu.txt "../tmp/building_color.tif"

