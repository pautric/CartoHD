from cartoHD import run_command, cartoHDprocess
import os
import logging


# TODO
# processing.run("terrain_shading:Shadow depth", {'INPUT':'/tmp/processing_RHeEYq/7b63e916c7dc48d1aeb658a89ca78558/OUTPUT.tif','DIRECTION':315,'ANGLE':10,'SMOOTH':True,'OUTPUT':'TEMPORARY_OUTPUT'})
"""

1 Non classé
2 Sol
3 Végétation basse (0-50 cm)
4 Végétation moyenne (50 cm-1,50 m)
5 Végétation haute (+1,50 m)
6 Bâtiment
9 Eau
17 Tablier de pont

64 Sursol pérenne
66 Points virtuels
67 Divers - bâtis

"""


def process_area(
    area_name: str,
    data_root: str,
    output_root: str,
    case: str,
    bounds: str = None,
    download: bool = True,
):
    """
    Downloads LiDAR data for a specific area and runs the CartoHD processing pipeline.

    This function automates the following steps:
    1. (Optional) Downloads LiDAR data files using a .txt file list.
    2. Defines input and output paths based on the area name.
    3. Calls the main `cartoHDprocess` function to generate map layers.
    4. Copies a QGIS project file template into the output directory.

    Args:
        area_name (str): The name of the area to process (e.g., "wam2025").
                         This is used to locate the data and create output folders.
        data_root (str): The root directory where LiDAR data is stored or will be downloaded to.
        output_root (str): The root directory where the processed output will be saved.
        case (str): The case identifier for processing (e.g., "FR" for France),
                    which determines the LiDAR classification codes to use.
        bounds (str, optional): A string representing the bounding box to crop the data,
                                e.g., "([xmin, xmax],[ymin, ymax])". Defaults to None.
        download (bool, optional): If True, attempts to download the data using wget.
                                   Defaults to True.
    """
    logging.info(f"--- Processing area: {area_name} ---")

    download_dir = os.path.join(data_root, area_name)
    download_list_file = os.path.join(data_root, f"{area_name}.txt")

    if download:
        logging.info("Downloading data...")
        os.makedirs(download_dir, exist_ok=True)
        run_command(["wget", "-i", download_list_file, "-nc", "-P", download_dir])

    input_lidar_data = os.path.join(download_dir, "*.laz")
    output_folder = os.path.join(output_root, area_name, "")  # Add trailing slash

    cartoHDprocess(input_lidar_data, output_folder, bounds=bounds, case=case)

    logging.info("Copying QGIS project file...")
    run_command(["cp", "src/project_FR.qgz", output_folder])
    logging.info(f"--- Finished processing {area_name} ---")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(funcName)s - %(message)s",
    )
    # Configuration for the processing job
    # 1. Set the root directory where your LiDAR data is stored.
    lidar_data_root = "/Users/pautric/Documents/20250917_CartoHD/lidar_Data/"

    # 2. Set the directory where the output maps will be saved.
    map_output_root = "/Users/pautric/Documents/20250917_CartoHD/lidar_Mapping/"

    # 3. List the area(s) to process. This should match the subfolder name in lidar_data_root.
    areas_to_process = ["colinesprovence"]

    for area in areas_to_process:
        # 4. Call the processing function. Set download=False since the file is local.
        process_area(area, lidar_data_root, map_output_root, case="FR", download=False)
