from lib import run_command, sequential_buffer_tiff

'''
target scale: 1:1000

test ambient oclusion - only for buildings
blurry water ?
more topo names ?
contour labels
test https://www.shadedrelief.com/texture_shading/

'''

process_dsm = False
process_dtm = True
process_vegetation = False
process_building = False
with_pdal_pipeline = True


# ensure pdal command is available through conda install
if with_pdal_pipeline: run_command(["conda", "activate", "pdal"])

if process_dsm:

    if with_pdal_pipeline:
        print("pipeline DSM")
        run_command(["pdal", "pipeline", "src/p_dsm.json"])

    #TODO: remove outliers
    #TODO: smooth ?

    print("fill dsm no data")
    #TODO: should not be linear
    run_command(["gdal_fillnodata.py", "-md", "20", "-of", "GTiff", "tmp/dsm_raw.tif", "tmp/dsm.tif"])

    print("dsm hillshading")
    run_command(["gdaldem", "hillshade", "tmp/dsm.tif", "tmp/hillshade.tif", "-z", "1", "-s", "1", "-az", "315", "-alt", "45"])

    print("dsm slope")
    run_command(["gdaldem", "slope", "tmp/dsm.tif", "tmp/slope.tif", "-s", "1"])

    #TODO: make shadows

if process_dtm:

    if with_pdal_pipeline:
        print("pipeline DTM")
        run_command(["pdal", "pipeline", "src/p_dtm.json"])


    print("fill dtm no data")
    #TODO: should not be linear
    run_command(["gdal_fillnodata.py", "-md", "20", "-of", "GTiff", "tmp/dtm_raw.tif", "tmp/dtm.tif"])

    print("smooth dtm")
    run_command(["gdal_filter", "-of", "GTiff", "-kernel", "smooth", "5x5", "-co", "COMPRESS=LZW", "tmp/dtm.tif", "tmp/dtm_smoothed.tif"])

    print("contour dtm")
    run_command(["gdal_contour", "-a", "elevation", "-i", "5", "tmp/dtm_smoothed.tif", "-f", "GPKG", "tmp/contours.gpkg"])


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
