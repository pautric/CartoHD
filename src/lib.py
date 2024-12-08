from math import hypot
import subprocess
import numpy as np
import rasterio
import geopandas as gpd
from scipy.ndimage import binary_dilation, gaussian_filter, binary_erosion, convolve
from rasterio.transform import from_origin



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







def compute_rayshading(input_file: str, output_file: str, light_azimuth: float = 315, light_altitude: float = 30, max: int = 100, jump: int = 10):
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
    with rasterio.open(input_file) as src:
        dem = src.read(1)  # Read DEM data
        #transform = src.transform  # Geospatial transform
        #pixel_size_x = transform[0]
        #pixel_size_y = -transform[4]

    # Dimensions of the DEM
    rows, cols = dem.shape

    # Convert light direction to radians
    azimuth_rad = np.radians(light_azimuth)
    altitude_rad = np.radians(light_altitude)

    # Calculate light direction vector
    dx = jump * np.sin(azimuth_rad)  # Light movement in x direction
    dy = jump * np.cos(azimuth_rad)  # Light movement in y direction
    dz = jump * np.tan(altitude_rad)  # Light movement in height

    # Normalize light direction for stepping
    #step_size = max(abs(dx), abs(dy))  # Ensure consistent stepping
    #dx /= step_size
    #dy /= step_size

    # Initialize output array
    #rayshaded = np.ones_like(dem, dtype=np.uint8)
    no_data_value = -9999
    rayshaded = np.full((rows, cols), no_data_value, dtype=np.int32)

    #print(rows, cols)
    #print(dx, dy, dz)

    # Ray-casting algorithm
    for row in range(rows):
        print(row, "/", rows)
        for col in range(cols):
            z0 = dem[row, col]
            shadow = no_data_value

            #print(row, col, z0)

            # Step along the ray direction
            x0, y0 = col + 0.5, row + 0.5  # Start at the center of the current pixel
            x,y,z = x0,y0,z0

            # project ray
            while 0 <= x < cols and 0 <= y < rows:
                x += dx
                y += dy
                z += dz

                distance = hypot(x-x0,y-y0,z-z0)
                if distance > max: break

                # Get the elevation of the pixel at (x, y) using bilinear interpolation
                x_floor, y_floor = int(np.floor(x)), int(np.floor(y))
                #x_ceil, y_ceil = int(np.ceil(x)), int(np.ceil(y))

                if 0 <= x_floor < cols and 0 <= y_floor < rows:
                    elevation = dem[y_floor, x_floor]  # Approximation (nearest neighbor)

                    # Check if this pixel blocks the current pixel
                    if elevation > z:
                        shadow = int(distance)
                        break

            rayshaded[row, col] = shadow

    # Save rayshaded result as GeoTIFF
    with rasterio.open(
        output_file,
        'w',
        driver='GTiff',
        height=rayshaded.shape[0],
        width=rayshaded.shape[1],
        count=1,
        dtype='uint8',
        crs=src.crs,
        transform=src.transform,
    ) as dst:
        dst.write(rayshaded, 1)

    print(f"Rayshaded relief saved to {output_file}")
    return rayshaded


# Example usage
compute_rayshading('/home/juju/Bureau/dsm.tif', '/home/juju/Bureau/shadow.tif', light_azimuth=315, light_altitude=30)

