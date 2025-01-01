from lib import run_command, sequential_buffer_tiff, smooth, contour_type_field, compute_rayshading
import os
import json


f = "niederanven"
# 
caseBE = False

input_lidar_data = "/home/juju/geodata/lidar/"+f+"/*.laz"
output_folder = "/home/juju/lidar_mapping/"+f+"/"
#xmin xmax ymin ymax
#"([0,1000000],[0,1000000])"
bounds = None #"([699000, 703000],[636000, 639000])"

codeBuilding = "1" if caseBE else "6"


#https://www.youtube.com/watch?v=ZcU6N2D0ZaI

process_dsm = True
process_dtm = True
process_vegetation = True
process_building = True
compute_dsm_rayshading = True
with_pdal_pipeline = True


#create necessary folders
os.makedirs(output_folder, exist_ok=True)
os.makedirs("tmp/", exist_ok=True)

# ensure pdal command is available through conda install
#if with_pdal_pipeline: run_command(["conda", "activate", "pdal"])



def get_base_config():
    # create base pdal config, to be completed for various cases
    data = [
  {
    "type": "readers.las",
    "filename": input_lidar_data
  }]
    if bounds: data.append({
        "type": "filters.crop",
        "bounds": bounds
    })
    return data




if process_dsm:

    if with_pdal_pipeline:
        # prepare PDAL pipeline config
        print("pipeline DSM")

        data = get_base_config()
        data.extend(
    [
        # remove noise
  {
    "limits": "Classification![7:7]",
    "type": "filters.range",
    "tag": "nonoise"
  },
    #TODO: remove outlier points ?
  # keep elevation value
  {
    "type": "filters.ferry",
    "dimensions": "Z=>elevation"
  },
  # max value for each 20cm pixel
  {
    "type": "writers.gdal",
    "filename": output_folder+"dsm_raw.tif",
    "resolution": 0.2,
    "output_type": "max"
  }
])

        # execute PDAL pipeline
        with open("tmp/p_dsm.json", "w") as f: json.dump(data, f, indent=3)
        run_command(["pdal", "pipeline", "tmp/p_dsm.json"])

    print("fill dsm no data")
    #TODO: should not be linear
    #TODO: smooth ?
    run_command(["gdal_fillnodata.py", "-md", "20", "-of", "GTiff", output_folder+"dsm_raw.tif", output_folder+"dsm.tif"])
    os.remove(output_folder+"dsm_raw.tif")

    #print("dsm hillshading")
    #run_command(["gdaldem", "hillshade", output_folder+"dsm.tif", output_folder+"hillshade_dsm.tif", "-z", "1", "-s", "1", "-az", "315", "-alt", "45"])

    print("dsm slope")
    run_command(["gdaldem", "slope", output_folder+"dsm.tif", output_folder+"slope_dsm.tif", "-s", "1"])


if process_dtm:

    if with_pdal_pipeline:
        # prepare PDAL pipeline config
        print("pipeline DTM")

        data = get_base_config()
        data.extend([

  {
      # keep one ground and building
    "type": "filters.range",
    "limits": "Classification[2:2],Classification["+codeBuilding+":"+codeBuilding+"]"
  },
  {
    "type": "writers.gdal",
    "filename": output_folder+"dtm_building.tif",
    "resolution": 0.2,
    "output_type": "min"
  },
  {
    "type": "filters.range",
    #keep only ground
    "limits": "Classification[2:2]"
  },
  {
      #keep only elevation
    "type": "filters.ferry",
    "dimensions": "Z=>elevation"
  },
  {
      #keep min, 20 centimeter resolution
    "type": "writers.gdal",
    "filename": output_folder+"dtm_raw.tif",
    "resolution": 0.2,
    "output_type": "min"
  }
])

        # execute PDAL pipeline
        with open("tmp/p_dtm.json", "w") as f: json.dump(data, f, indent=3)
        run_command(["pdal", "pipeline", "tmp/p_dtm.json"])


    print("dtm slope")
    run_command(["gdaldem", "slope", output_folder+"dtm_raw.tif", output_folder+"slope_dtm.tif", "-s", "1"])

    print("dtm building slope")
    run_command(["gdaldem", "slope", output_folder+"dtm_building.tif", output_folder+"slope_dtm_building.tif", "-s", "1"])

    print("fill dtm no data")
    run_command(["gdal_fillnodata.py", "-md", "50", "-of", "GTiff", output_folder+"dtm_raw.tif", output_folder+"dtm.tif"])
    os.remove(output_folder+"dtm_raw.tif")

    print("smooth dtm")
    smooth(output_folder+"dtm.tif", output_folder+"dtm_smoothed.tif", 6)
    #os.remove(output_folder+"dtm.tif")

    print("make contours")
    run_command(["gdal_contour", "-a", "elevation", "-i", "1", output_folder+"dtm_smoothed.tif", "-f", "GPKG", output_folder+"contours.gpkg"])
    os.remove(output_folder+"dtm_smoothed.tif")

    print("set contours type")
    contour_type_field(output_folder+"contours.gpkg", "contour")

if process_vegetation:

    if with_pdal_pipeline:
        # prepare PDAL pipeline config
        print("pipeline vegetation")

        data = get_base_config()
        data.extend([
    {
        #keep only vegetation
        "type": "filters.range",
        "limits": "Classification[3:5]"
    },


    # still necessary ?
    {
        "type": "filters.ferry",
        "dimensions": "Z=>elevation"
    },
    {
        "type": "writers.gdal",
        "filename": output_folder+"dsm_vegetation.tif",
        "resolution": 0.2,
        "output_type": "max"
    },


    {
        "type": "filters.assign",
        "assignment": "Z[:]=1"
    },
    {
        "type": "writers.gdal",
        "filename": output_folder+"vegetation.tif",
        "dimension": "Z",
        "output_type": "max",
        "resolution": 0.2
    }
])

        # execute PDAL pipeline
        with open("tmp/p_vegetation.json", "w") as f: json.dump(data, f, indent=3)
        run_command(["pdal", "pipeline", "tmp/p_vegetation.json"])

    #print("vegetation slope")
    #run_command(["gdaldem", "slope", output_folder+"dsm_vegetation.tif", output_folder+"slope_vegetation.tif", "-s", "1"])

    #TODO vectorise ? To make blurry outline ?

    print("clean vegetation.tif")
    sequential_buffer_tiff(output_folder+"vegetation.tif", output_folder+"vegetation_clean.tif", [-2, 2])
    os.remove(output_folder+"vegetation.tif")

if process_building:

    if with_pdal_pipeline:
        # prepare PDAL pipeline config
        print("pipeline building")

        data = get_base_config()
        data.extend([
    {
        "type": "filters.range",
        "limits": "Classification["+codeBuilding+":"+codeBuilding+"]"
    },
    {
        "type": "filters.ferry",
        "dimensions": "Z=>elevation"
    },
    {
        "type": "writers.gdal",
        "filename": output_folder+"dsm_building.tif",
        "resolution": 0.2,
        "output_type": "max"
    },
    {
        "type": "filters.assign",
        "assignment": "Z[:]=1"
    },
    {
        "type": "writers.gdal",
        "filename": output_folder+"building.tif",
        "dimension": "Z",
        "output_type": "max",
        "resolution": 0.2
    }
])

        # execute PDAL pipeline
        with open("tmp/p_building.json", "w") as f: json.dump(data, f, indent=3)
        run_command(["pdal", "pipeline", "tmp/p_building.json"])


    #print("building slope")
    #run_command(["gdaldem", "slope", output_folder+"dsm_building.tif", output_folder+"slope_building.tif", "-s", "1"])

    print("clean building.tif")
    sequential_buffer_tiff(output_folder+"building.tif", output_folder+"building_clean.tif", [3, -3])
    os.remove(output_folder+"building.tif")


    print("vectorise")
    run_command(["gdal_polygonize.py", "-overwrite", output_folder+"building_clean.tif", "-f", "GPKG", output_folder+"building.gpkg"])
    os.remove(output_folder+"building_clean.tif")

    print("simplify")
    run_command(["ogr2ogr", "-f", "GPKG", "-overwrite", output_folder+"building_simplified.gpkg", output_folder+"building.gpkg", "-simplify", "0.5"])
    os.remove(output_folder+"building.gpkg")



if compute_dsm_rayshading:
    print("ray shading")

    compute_rayshading(output_folder+"dsm.tif", output_folder+"shadow.tif", light_altitude=15)


#TODO
#processing.run("terrain_shading:Shadow depth", {'INPUT':'/tmp/processing_RHeEYq/7b63e916c7dc48d1aeb658a89ca78558/OUTPUT.tif','DIRECTION':315,'ANGLE':10,'SMOOTH':True,'OUTPUT':'TEMPORARY_OUTPUT'})

