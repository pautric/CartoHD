
echo "pipeline vege"
pdal pipeline p_veg.json

echo "color vege"
gdaldem color-relief "../tmp/vegetation.tif" -of GTiff -alpha color_table_vege.txt "../tmp/vegetation_color.tif"


echo "pipeline bu"
pdal pipeline p_bu.json

echo "color bu"
gdaldem color-relief "../tmp/building.tif" -of GTiff -alpha color_table_bu.txt "../tmp/building_color.tif"
