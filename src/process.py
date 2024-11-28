import pdal
import json


tiles = "/home/juju/Bureau/lidar_test/tiles/*.laz"
outfolder = "../tmp/"


# Define the PDAL pipeline as a JSON string
pipeline = [
    {
        "type": "readers.las",
        "filename": 
    },
    {
        "limits": "Classification![7:7]",
        "type": "filters.range",
        "tag": "nonoise"
    },
    {
        "type": "filters.ferry",
        "dimensions": "Z=>elevation"
    },
    {
        "type": "writers.gdal",
        "filename:" + outfolder + "dsm_raw.tif",
        "resolution": 0.2,
        "output_type": "max"
    }
]

pipeline_json = json.dumps(pipeline)
pipeline_obj = pdal.Pipeline(pipeline_json)
pipeline_obj.execute()

log = pipeline_obj.log
print(log)

