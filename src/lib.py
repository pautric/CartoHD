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








def calculate_shadow(input_tiff, output_tiff, azimuth = 315, elevation_angle = 30):
    """
    Calculate the shadow map for a given DSM based on solar azimuth and elevation angle.

    Parameters:
        input_tiff: str, path to the input DSM file (TIFF).
        output_tiff: str, path to the output shadow map file (TIFF).
        azimuth: float, solar azimuth angle in degrees.
        elevation_angle: float, solar elevation angle in degrees.
    """
    # Load DSM data
    with rasterio.open(input_tiff) as dataset:
        dsm = dataset.read(1)
        resolution = dataset.res[0]
        transform = dataset.transform

    rows, cols = dsm.shape
    shadow_map = np.ones_like(dsm, dtype=np.float32)  # Start with all pixels sunlit

    # angles to radians
    azimuth_rad = np.radians(azimuth)
    elevation_rad = np.radians(elevation_angle)

    # sun direction components
    dx = np.sin(azimuth_rad)
    dy = np.cos(azimuth_rad)
    dz = np.tan(elevation_rad)

    # check for shadow for each pixel
    for i in range(rows):
        for j in range(cols):
            x, y, z = j, i, dsm[i, j]
            shadow = False

            # ray in sun direction
            while 0 <= x < cols and 0 <= y < rows:
                x += dx
                y += dy
                z += dz * resolution  # elevation increases along the ray

                # nearest pixel
                x_idx, y_idx = int(round(x)), int(round(y))
                if 0 <= x_idx < cols and 0 <= y_idx < rows:
                    if dsm[y_idx, x_idx] > z:  # shadow detected
                        shadow = True
                        break

            # mark as shadowed
            if shadow: shadow_map[i, j] = 0

    # save
    with rasterio.open(output_tiff, 'w', driver='GTiff', count=1, dtype='float32',
                       width=cols, height=rows, crs=dataset.crs, transform=transform) as out_dataset:
        out_dataset.write(shadow_map, 1)













def calculate_shadowXXX(input_tiff, output_tiff, direction = 315, sun_angle = 30, smooth=False):
    """
    Simulate natural shadow over a raster DEM (Digital Elevation Model).
    
    Parameters:
        input_tiff (str): Path to the input DEM TIFF file.
        output_tiff (str): Path to save the output shadow map (TIFF file).
        direction (float): Sun direction (azimuth) in degrees (0 to 360°).
        sun_angle (float): Sun angle (elevation angle) in degrees (0 to 90°).
        smooth (bool): Whether to apply a smoothing filter to the output (default: False).
    """
    # Open the input DEM raster file using rasterio
    with rasterio.open(input_tiff) as src:
        dem = src.read(1)  # Read the DEM as a 2D array (first band)
        transform = src.transform  # Affine transform (georeferencing)
        nodata_value = src.nodata  # NoData value (if present)

        if nodata_value is None:
            nodata_value = -9999  # Set a default NoData value if not set in the original DEM

        # Mask out NoData values
        dem[dem == nodata_value] = np.nan

    # Calculate the sun direction components (dx, dy, dz)
    direction_rad = np.radians(direction)
    sun_angle_rad = np.radians(sun_angle)
    dx = np.sin(direction_rad)  # Horizontal component
    dy = np.cos(direction_rad)  # Horizontal component
    dz = np.tan(sun_angle_rad)  # Vertical component

    # Get the shape of the DEM (rows, cols)
    rows, cols = dem.shape

    # Create an empty array to store shadow depth values
    shadow_map = np.ones_like(dem) * np.nan  # Initially set all to NaN

    # Calculate shadow depth for each pixel based on the sun's position
    for row in range(rows):
        for col in range(cols):
            if np.isnan(dem[row, col]):
                continue  # Skip NoData values
            
            # Determine the shadow distance for each pixel
            shadow_depth = 0
            x, y = col, row
            while True:
                x += dx
                y -= dy
                shadow_depth += dz

                # Check bounds
                if x < 0 or x >= cols or y < 0 or y >= rows:
                    break

                if np.isnan(dem[int(y), int(x)]):
                    break  # Stop if the ray leaves the DEM or hits NoData
                
                # Check if the surface blocks the shadow
                if dem[int(y), int(x)] > dem[row, col] + shadow_depth:
                    shadow_map[row, col] = shadow_depth
                    break
    
    # Apply smoothing filter if requested
    if smooth:
        kernel = np.ones((3, 3)) / 9  # 3x3 averaging kernel
        shadow_map = convolve(shadow_map, kernel, mode='nearest')

    # Write the shadow map to the output TIFF file using rasterio
    with rasterio.open(output_tiff, 'w', driver='GTiff',
                       height=rows, width=cols,
                       count=1, dtype='float32',
                       crs=src.crs, transform=transform) as dst:
        dst.write(shadow_map, 1)
        dst.set_nodata(nodata_value)




#calculate_shadowXXX("tmp/dsm.tif", "tmp/ZZZ_shadow.tif")




















#TODO test !


def compute_rayshading(input_file: str, output_file: str, light_azimuth: float = 315, light_altitude: float = 30, max: int = 100):
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
    dx = np.sin(azimuth_rad)  # Light movement in x direction
    dy = np.cos(azimuth_rad)  # Light movement in y direction
    dz = np.tan(altitude_rad)  # Light movement in height

    # Normalize light direction for stepping
    #step_size = max(abs(dx), abs(dy))  # Ensure consistent stepping
    #dx /= step_size
    #dy /= step_size

    # Initialize output array
    rayshaded = np.ones_like(dem, dtype=np.uint8)  # 1 = illuminated, 0 = shadowed

    #print(rows, cols)
    #print(dx, dy, dz)

    # Ray-casting algorithm
    for row in range(rows):
        print(row)
        for col in range(cols):
            z0 = dem[row, col]
            shadowed = False

            #print(row, col, z0)

            # Step along the ray direction
            x0, y0 = col + 0.5, row + 0.5  # Start at the center of the current pixel
            x,y,z = x0,y0,z0

            while 0 <= x < cols and 0 <= y < rows:
                x += dx
                y += dy
                z += dz #* step_size

                distance = hypot(x-x0,y-y0,z-z0)
                if distance > max: break

                # Get the elevation of the pixel at (x, y) using bilinear interpolation
                x_floor, y_floor = int(np.floor(x)), int(np.floor(y))
                #x_ceil, y_ceil = int(np.ceil(x)), int(np.ceil(y))

                if 0 <= x_floor < cols and 0 <= y_floor < rows:
                    elevation = dem[y_floor, x_floor]  # Approximation (nearest neighbor)

                    # Check if this pixel blocks the current pixel
                    if elevation > z:
                        shadowed = True
                        break

            rayshaded[row, col] = 0 if shadowed else 1  # Mark shadowed pixels

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






#TODO test !

def compute_rayshading2(input_file: str, output_file: str, light_azimuth: float = 315, light_altitude: float = 45):
    """
    Compute ray shading from a DEM (Digital Elevation Model) in GeoTIFF format.
    
    Each pixel's shadow is calculated by checking if higher elevation pixels along 
    the sun's ray path block the sunlight.

    Parameters:
    -----------
    input_file : str
        Path to the input DEM file (GeoTIFF).
    output_file : str
        Path where the output shaded relief image will be saved.
    light_azimuth : float
        Azimuth of the light source in degrees (0-360, with 0=N, 90=E, 180=S, 270=W). Default is 315° (NW).
    light_altitude : float
        Altitude of the light source in degrees above the horizon (0-90). Default is 45°.
    """
    with rasterio.open(input_file) as src:
        dem = src.read(1).astype(float)  # Elevation data
        transform = src.transform
        resolution_x = transform[0]
        resolution_y = -transform[4]  # y-axis resolution (negative in GeoTIFF)
    
    nrows, ncols = dem.shape
    shadow = np.ones((nrows, ncols), dtype=np.uint8) * 255  # Start with full illumination (white = illuminated)

    # Convert light direction to radians
    azimuth_rad = np.radians(light_azimuth)
    altitude_rad = np.radians(light_altitude)
    
    # Calculate the unit vector of the sun ray
    dx = np.sin(azimuth_rad)
    dy = np.cos(azimuth_rad)
    dz = np.tan(altitude_rad)
    
    for i in range(nrows):
        for j in range(ncols):
            # Position of the current pixel in real-world coordinates
            #x0 = j * resolution_x
            #y0 = i * resolution_y
            z0 = dem[i, j]

            # Ray tracing variables
            x, y = j, i  # Pixel indices in the array
            distance = 0

            while True:
                # Move along the ray in the direction of (dx, dy)
                x += dx
                y += dy
                distance += 1

                # Get the nearest pixel indices
                xi, yi = int(round(x)), int(round(y))

                # Check if the pixel is outside the bounds
                if xi < 0 or yi < 0 or xi >= ncols or yi >= nrows:
                    break
                
                # Calculate the height of the sun ray at this point
                height_of_sun_ray = z0 + distance * dz
                
                # Get the elevation of the current pixel along the ray
                elevation_at_pixel = dem[yi, xi]

                # Check if the current pixel blocks the sun ray
                if elevation_at_pixel > height_of_sun_ray:
                    shadow[i, j] = 0  # Pixel is in shadow (black = shadow)
                    break
    
    # Save the shadow map as a GeoTIFF
    with rasterio.open(
        output_file,
        'w',
        driver='GTiff',
        height=shadow.shape[0],
        width=shadow.shape[1],
        count=1,
        dtype='uint8',
        crs=src.crs,
        transform=src.transform,
    ) as dst:
        dst.write(shadow, 1)
    
    print(f"Shadow map saved to {output_file}")
    return shadow

