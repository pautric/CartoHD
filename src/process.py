from lib import run_command, sequential_buffer_tiff

'''
target scale: 1:1000

test ambient oclusion - only for buildings
blurry water ?
more topo names ?
contour labels
test https://www.shadedrelief.com/texture_shading/

'''

process_dsm = True
process_dtm = True
process_vegetation = True
process_building = True
with_pdal_pipeline = True


# ensure pdal command is available through conda install
if with_pdal_pipeline: run_command(["conda", "activate", "pdal"])

if process_dsm:

    if with_pdal_pipeline:
        print("pipeline DSM")
        run_command(["pdal", "pipeline", "src/p_dsm.json"])

    #TODO: remove outliers
    #TODO: smooth ?

    print("fill no data")
    #TODO: should not be linear
    run_command(["gdal_fillnodata.py", "-md", "20", "-of", "GTiff", "tmp/dsm_raw.tif", "tmp/dsm.tif"])

    print("hillshading")
    run_command(["gdaldem", "hillshade", "tmp/dsm.tif", "tmp/hillshade.tif", "-z", "1", "-s", "1", "-az", "315", "-alt", "45"])

    print("slope")
    run_command(["gdaldem", "slope", "tmp/dsm.tif", "tmp/slope.tif", "-s", "1"])

    #TODO: make shadows

if process_dtm:
    #make contours
    #TODO use pullauta ?
    pass


if process_vegetation:

    if with_pdal_pipeline:
        print("pipeline vegetation")
        run_command(["pdal", "pipeline", "src/p_vegetation.json"])

    #TODO vectorise ? To make blurry outline ?

    print("clean vegetation.tif")
    sequential_buffer_tiff("tmp/vegetation.tif", "tmp/vegetation_clean.tif", [-2, 2])

if process_building:

    if with_pdal_pipeline:
        print("pipeline building")
        run_command(["pdal", "pipeline", "src/p_building.json"])

    print("clean building.tif")
    sequential_buffer_tiff("tmp/building.tif", "tmp/building_clean.tif", [3, -3])

    print("vectorise")
    run_command(["gdal_polygonize.py", "tmp/building_clean.tif", "-f", "GPKG", "tmp/building.gpkg"])

    print("simplify")
    run_command(["ogr2ogr", "-f", "GPKG", "tmp/building_simplified.gpkg", "tmp/building.gpkg", "-simplify", "1"])
