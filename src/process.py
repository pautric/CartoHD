from lib import run_command, cartoHD
import os



#TODO
#processing.run("terrain_shading:Shadow depth", {'INPUT':'/tmp/processing_RHeEYq/7b63e916c7dc48d1aeb658a89ca78558/OUTPUT.tif','DIRECTION':315,'ANGLE':10,'SMOOTH':True,'OUTPUT':'TEMPORARY_OUTPUT'})
#See https://www.youtube.com/watch?v=ZcU6N2D0ZaI


idf = "/home/juju/geodata/lidar/"
for f in ["dune_pilat", "cirque_gavarnie", "aix_en_provence", "banyuls", "crest", "toulon", "guillestre", "lyon", "bourges", "hk"]:
    # "villandry", "ile_aix", "larzac", "mont_blanc", 
    print(f)

    #if(f != "dune_pilat"):
    print("download")
    os.makedirs(idf+f+"/", exist_ok=True)
    run_command(["wget", "-i", idf+f+".txt", "-P", idf+f+"/"])

    input_lidar_data = idf+f+"/*.laz"
    output_folder = "/home/juju/lidar_mapping/"+f+"/"
    #xmin xmax ymin ymax
    bounds = None #"([699000, 703000],[636000, 639000])"

    cartoHD(input_lidar_data, output_folder, bounds = bounds)

    print("copy QGIS project file")
    run_command(["cp", "src/project_FR.qgz", output_folder])

