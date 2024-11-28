import subprocess

from buffering import run_command, sequential_buffer_tiff

process_dsm = False
process_vegetation = True
process_building = False


if process_dsm:

    print("pipeline DSM")
    run_command(["pdal", "pipeline", "src/p_dsm.json"])

    print("fill no data")
    #TODO: should not be linear
    run_command("gdal_fillnodata.py -md 20 -of GTiff ../tmp/dsm_raw.tif ../tmp/dsm.tif")

    print("hillshading")
    run_command("gdaldem hillshade ../tmp/dsm.tif ../tmp/hillshade.tif -z 1 -s 1 -az 315 -alt 45")

    print("slope")
    run_command("gdaldem slope ../tmp/dsm.tif ../tmp/slope.tif -s 1")

    #TODO: make shadows

if process_vegetation:

    print("pipeline vegetation")
    run_command(["pdal", "pipeline", "src/p_vegetation.json"])
    #TODO vectorise ?

    print("clean vegetation.tif")
    sequential_buffer_tiff("tmp/vegetation.tif", "tmp/vegetation_clean.tif", [-2, 2])

if process_building:

    print("pipeline building")
    run_command(["pdal", "pipeline", "src/p_building.json"])
    #TODO vectorise ?

    print("clean building.tif")
    sequential_buffer_tiff("tmp/building.tif", "tmp/building_clean.tif", [3, -3])


