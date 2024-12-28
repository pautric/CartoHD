import math
from math import ceil, hypot, floor
import subprocess
import numpy as np
import rasterio
import geopandas as gpd
from scipy.ndimage import binary_dilation, gaussian_filter, binary_erosion, convolve



def run_command(command):
    result = subprocess.run(command, capture_output=True, text=True)
    if result.stdout: print(result.stdout)
    if result.stderr:
        print("Error:", result.stderr)



def buffer_tiff(input_path, output_path, buffer_distance):
    """
    Buffers pixels with value 1 in a TIFF image. 
    Supports both positive (expansion) and negative (shrinkage) buffer distances.

    Parameters:
        input_path (str): Path to the input TIFF file.
        output_path (str): Path to save the output buffered TIFF file.
        buffer_distance (int): Number of pixels to buffer.
                               Positive values expand, negative values shrink.
    """
    # Open the TIFF file
    with rasterio.open(input_path) as src:
        data = src.read(1)  # Read the first band
        no_data_value = src.nodata
        
        if no_data_value is None:
            raise ValueError("Input TIFF file does not specify a 'no_data' value.")

        # Create a mask of pixels with value 1
        valid_data_mask = data == 1

        # Generate a structuring element for the operation
        abs_buffer_distance = abs(buffer_distance)
        structure = np.ones((2 * abs_buffer_distance + 1, 2 * abs_buffer_distance + 1))

        # Apply the appropriate operation
        if buffer_distance > 0:
            # Positive buffer (expansion)
            buffered_mask = binary_dilation(valid_data_mask, structure=structure)
        elif buffer_distance < 0:
            # Negative buffer (shrinkage)
            buffered_mask = binary_erosion(valid_data_mask, structure=structure)
        else:
            # No buffer, keep the original
            buffered_mask = valid_data_mask

        # Create a new array, keeping 'no_data_value' in the background
        buffered_data = np.where(buffered_mask, 1, no_data_value)

        # Save the buffered result
        with rasterio.open(
            output_path,
            "w",
            driver="GTiff",
            height=data.shape[0],
            width=data.shape[1],
            count=1,
            dtype=data.dtype,
            crs=src.crs,
            transform=src.transform,
            nodata=no_data_value
        ) as dst:
            dst.write(buffered_data, 1)


def sequential_buffer_tiff(input_path, output_path, buffer_distances):
    """
    Applies a sequence of buffer operations (both positive and negative) on a TIFF image.

    Parameters:
        input_path (str): Path to the input TIFF file.
        output_path (str): Path to save the final buffered TIFF file.
        buffer_distances (list of int): List of buffer distances - in pixel number !!! (positive for expansion, negative for shrinking).
    """
    with rasterio.open(input_path) as src:
        data = src.read(1)  # Read the first band
        no_data_value = src.nodata
        
        if no_data_value is None:
            raise ValueError("Input TIFF file does not specify a 'no_data' value.")

        # Create a mask of pixels with value 1
        current_mask = data == 1

        # Apply each buffer operation sequentially
        for buffer_distance in buffer_distances:
            abs_buffer_distance = abs(buffer_distance)
            structure = np.ones((2 * abs_buffer_distance + 1, 2 * abs_buffer_distance + 1))

            if buffer_distance > 0:
                # Positive buffer (expansion)
                current_mask = binary_dilation(current_mask, structure=structure)
            elif buffer_distance < 0:
                # Negative buffer (shrinkage)
                current_mask = binary_erosion(current_mask, structure=structure)
            # If buffer_distance == 0, skip (no operation for zero buffer)

        # Create the final array, keeping 'no_data_value' in the background
        final_data = np.where(current_mask, 1, no_data_value)

        # Save the final result
        with rasterio.open(
            output_path,
            "w",
            driver="GTiff",
            height=data.shape[0],
            width=data.shape[1],
            count=1,
            dtype=data.dtype,
            crs=src.crs,
            transform=src.transform,
            nodata=no_data_value
        ) as dst:
            dst.write(final_data, 1)



def smooth(input_file, output_file, sigma):
    """
    Apply kernel smoothing to a TIFF

    Parameters:
    - input_file: str, path to the input DTM GeoTIFF file.
    - output_file: str, path to save the smoothed DTM GeoTIFF file.
    - sigma: float, standard deviation for Gaussian kernel.

    Returns:
    - None
    """

    with rasterio.open(input_file) as src:
        dtm = src.read(1, masked=True)
        profile = src.profile

        # Apply Gaussian smoothing
        smoothed_dtm = gaussian_filter(dtm.filled(np.nan), sigma=sigma)

        # Replace masked nodata regions with original nodata value
        smoothed_dtm = np.where(dtm.mask, profile['nodata'], smoothed_dtm)

    # Update the profile for output
    profile.update(dtype=rasterio.float32, count=1, compress='lzw')

    # Save the smoothed DTM
    with rasterio.open(output_file, 'w', **profile) as dst:
        dst.write(smoothed_dtm.astype(rasterio.float32), 1)


def contour_type_field(input_file, layer_name, output_file=None):

    gdf = gpd.read_file(input_file, layer=layer_name)
    gdf['type'] = gdf['elevation'].apply(lambda x: 'index' if x % 5 == 0 else 'normal')
    if output_file is None: output_file = input_file
    gdf.to_file(output_file, layer=layer_name, driver="GPKG")







def compute_rayshading(input_file: str, output_file: str, light_azimuth: float = 315, light_altitude: float = 30, ray_max_length: int = None, jump: int = 1, show_progress: bool = False):
    """
    Compute rayshading for a DEM using a ray-casting algorithm.

    Parameters:
    -----------
    input_file : str
        Path to the input DEM file (GeoTIFF).
    output_file : str
        Path where the output shaded relief image will be saved.
    light_azimuth : float
        Azimuth of the light source in degrees (0-360, 0=N, 90=E, 180=S, 270=W).
    light_altitude : float
        Altitude of the light source in degrees above the horizon (0-90).

    Returns:
    --------
    rayshaded : np.ndarray
        The computed rayshaded image (0=shadow, 1=illuminated).
    """

    # Read input DEM
    with rasterio.open(input_file) as src: dem = src.read(1)
    # Get dimensions
    rows, cols = dem.shape

    # Initialize output array
    #rayshaded = np.ones_like(dem, dtype=np.uint8)
    no_data_value = 0
    rayshaded = np.full((rows, cols), no_data_value, dtype=np.uint16)


    # Calculate light direction vector
    azimuth_rad = (90 - light_azimuth + 180)*math.pi/180
    dx = jump * math.cos(azimuth_rad)
    dy = jump * math.sin(azimuth_rad)
    altitude_rad = light_altitude*math.pi/180
    dz = jump * math.tan(altitude_rad)

    # go through each pixel. From each one, make a ray and shade cells under until ray is stopped
    for row in range(rows):
        if show_progress: print(row, "/", (rows-1))
        for col in range(cols):

            #ray origin point
            x0, y0 = col + 0.5, row + 0.5
            z0 = dem[row, col]

            if z0 == src.nodata: continue

            # project ray
            x,y,z = x0,y0,z0
            while 0 <= x < cols and 0 <= y < rows:
                x += dx
                y -= dy
                z -= dz

                # compute ray length
                ray_length = hypot(x-x0, y-y0, z-z0)
                if ray_max_length != None and ray_length > ray_max_length: break

                col_, row_ = int(floor(x)), int(floor(y))

                # ray has reached image bounds: break
                if not (0 <= col_ < cols and 0 <= row_ < rows): break

                # if ray was blocked, break
                elevation = dem[row_, col_]
                if elevation == src.nodata: continue
                if elevation > z: break

                # get current shade value
                shade = rayshaded[row_, col_]
                ray_length = int(ceil(ray_length))

                # if no shade, set distance
                if shade == no_data_value: rayshaded[row_, col_] = ray_length
                # else set min distance
                else: rayshaded[row_, col_] = min(ray_length, shade)

    # Save rayshaded result as GeoTIFF
    with rasterio.open(
        output_file,
        'w',
        driver='GTiff',
        height=rayshaded.shape[0],
        width=rayshaded.shape[1],
        count=1,
        dtype='uint16',
        nodata=no_data_value,
        crs=src.crs,
        transform=src.transform,
    ) as dst:
        dst.write(rayshaded, 1)

    print(f"Rayshaded relief saved to {output_file}")
    return rayshaded


#compute_rayshading("/home/juju/lidar_mapping/strasbourg_cathedrale/dsm.tif", "/home/juju/lidar_mapping/strasbourg_cathedrale/shadow_2.tif")
'''
for a in ["arcon", "hauterives", "marseille_centre"]:
    print(a)
    compute_rayshading("/home/juju/lidar_mapping/"+a+"/dsm.tif", "/home/juju/lidar_mapping/"+a+"/shadow.tif", light_altitude = 15)

for angle in [10, 20,30,40,50,60]:
    print(angle)
    compute_rayshading("/home/juju/lidar_mapping/strasbourg_cathedrale/dsm.tif", "/home/juju/lidar_mapping/strasbourg_cathedrale/shadow_"+str(angle)+".tif", light_altitude = angle)
'''

#compute_rayshading('/home/juju/Bureau/dsm.tif', '/home/juju/Bureau/shadow.tif', light_azimuth=315, light_altitude=30)

