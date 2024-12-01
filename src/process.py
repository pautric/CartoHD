from lib import run_command, sequential_buffer_tiff, smooth, contour_type_field
import os


'''
test ambient oclusion - only for buildings
contour labels
test https://www.shadedrelief.com/texture_shading/

'''

process_dsm = True
process_dtm = True
process_vegetation = True
process_building = True
with_pdal_pipeline = True

input_folder = ""
output_folder = "tmp/"

# ensure pdal command is available through conda install
#if with_pdal_pipeline: run_command(["conda", "activate", "pdal"])

if process_dsm:

    if with_pdal_pipeline:
        print("pipeline DSM")
        run_command(["pdal", "pipeline", "src/p_dsm.json"])

    #TODO: remove outliers

    print("fill dsm no data")
    #TODO: should not be linear
    #TODO: smooth ?
    run_command(["gdal_fillnodata.py", "-md", "20", "-of", "GTiff", output_folder+"dsm_raw.tif", output_folder+"dsm.tif"])
    os.remove(output_folder+"dsm_raw.tif")

    print("dsm hillshading")
    run_command(["gdaldem", "hillshade", output_folder+"dsm.tif", output_folder+"hillshade_dsm.tif", "-z", "1", "-s", "1", "-az", "315", "-alt", "45"])

    print("dsm slope")
    run_command(["gdaldem", "slope", output_folder+"dsm.tif", output_folder+"slope_dsm.tif", "-s", "1"])

    #TODO: make shadow depth

if process_dtm:

    if with_pdal_pipeline:
        print("pipeline DTM")
        run_command(["pdal", "pipeline", "src/p_dtm.json"])

    print("fill dtm no data")
    run_command(["gdal_fillnodata.py", "-md", "50", "-of", "GTiff", output_folder+"dtm_raw.tif", output_folder+"dtm.tif"])
    os.remove(output_folder+"dtm_raw.tif")

    print("dtm slope")
    run_command(["gdaldem", "slope", output_folder+"dtm_raw.tif", output_folder+"slope_dtm.tif", "-s", "1"])

    print("smooth dtm")
    smooth(output_folder+"dtm.tif", output_folder+"dtm_smoothed.tif", 6)
    os.remove(output_folder+"dtm.tif")

    print("make contours")
    run_command(["gdal_contour", "-a", "elevation", "-i", "1", output_folder+"dtm_smoothed.tif", "-f", "GPKG", output_folder+"contours.gpkg"])
    os.remove(output_folder+"dtm_smoothed.tif")

    print("set contours type")
    contour_type_field(output_folder+"contours.gpkg", "contour")

if process_vegetation:

    if with_pdal_pipeline:
        print("pipeline vegetation")
        run_command(["pdal", "pipeline", "src/p_vegetation.json"])

    #TODO vectorise ? To make blurry outline ?

    print("clean vegetation.tif")
    sequential_buffer_tiff(output_folder+"vegetation.tif", output_folder+"vegetation_clean.tif", [-2, 2])
    os.remove(output_folder+"vegetation.tif")

if process_building:

    if with_pdal_pipeline:
        print("pipeline building")
        run_command(["pdal", "pipeline", "src/p_building.json"])

    print("clean building.tif")
    sequential_buffer_tiff(output_folder+"building.tif", output_folder+"building_clean.tif", [3, -3])
    os.remove(output_folder+"building.tif")

    print("vectorise")
    run_command(["gdal_polygonize.py", "-overwrite", output_folder+"building_clean.tif", "-f", "GPKG", output_folder+"building.gpkg"])
    os.remove(output_folder+"building_clean.tif")

    print("simplify")
    run_command(["ogr2ogr", "-f", "GPKG", "-overwrite", output_folder+"building_simplified.gpkg", output_folder+"building.gpkg", "-simplify", "0.5"])
    os.remove(output_folder+"building.tif")

