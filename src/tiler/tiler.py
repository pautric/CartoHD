import os
import math
import rasterio
from rasterio.enums import Resampling
from rasterio.windows import Window
from PIL import Image


def create_tile_directory(output_dir, zoom, x, y):
    """Create the necessary directories for storing the tile."""
    tile_path = os.path.join(output_dir, str(zoom), str(x))
    os.makedirs(tile_path, exist_ok=True)
    return os.path.join(tile_path, f"{y}.png")


def reproject(input_path, output_epsg, output_path):
    """Reproject raster."""
    import subprocess
    subprocess.run([
        'gdalwarp',
        '-t_srs', 'EPSG:' + output_epsg,
        input_path, output_path
    ])


def tile_raster(input_path, output_dir, min_zoom=13, max_zoom=15, tile_size=256, origin_x=0, origin_y=0):
    """
    Generate XYZ tiles from a raster in EPSG:2169 for the specified zoom levels.

    Args:
        input_path (str): Path to the input GeoTIFF file.
        output_dir (str): Directory to store the tiles.
        min_zoom (int): Minimum zoom level (e.g., 13).
        max_zoom (int): Maximum zoom level (e.g., 15).
        tile_size (int): Size of the tiles (typically 256).
        origin_x (int): X coordinate of the tiling scheme origin.
        origin_y (int): Y coordinate of the tiling scheme origin.
    """
    with rasterio.open(input_path) as src:
        
        # Get the raster bounds in EPSG:2169
        #left, bottom, right, top = src.bounds

        for zoom in range(min_zoom, max_zoom + 1):
            # Calculate the resolution for the zoom level
            scale_factor = 2 ** (max_zoom - zoom)
            
            width = int(src.width / scale_factor)
            height = int(src.height / scale_factor)
            
            print(f"Processing Zoom Level {zoom}: Width={width}, Height={height}")

            # Calculate how many tiles are required at this zoom level
            x_tiles = math.ceil(width / tile_size)
            y_tiles = math.ceil(height / tile_size)

            for x in range(x_tiles):
                for y in range(y_tiles):
                    
                    # Calculate pixel coordinates of the tile in the downsampled raster
                    window = Window(
                        col_off=(x * tile_size + origin_x) * scale_factor,
                        row_off=(y * tile_size + origin_y) * scale_factor,
                        width=tile_size * scale_factor,
                        height=tile_size * scale_factor
                    )
                    
                    # Read and resample the tile
                    tile_data = src.read(
                        out_shape=(
                            src.count,
                            tile_size,
                            tile_size
                        ),
                        window=window,
                        resampling=Resampling.nearest
                    )
                    
                    # Transpose to channels last for PIL (from (band, height, width) to (height, width, band))
                    tile_data = tile_data.transpose(1, 2, 0)
                    
                    # Normalize the pixel values to 8-bit (if not already 8-bit)
                    if tile_data.dtype != 'uint8':
                        tile_data = ((tile_data - tile_data.min()) / (tile_data.max() - tile_data.min()) * 255).astype('uint8')
                    
                    # Save as PNG
                    tile_path = create_tile_directory(output_dir, zoom, x, y)
                    
                    if tile_data.shape[2] == 1:  # Single band (grayscale)
                        Image.fromarray(tile_data[:, :, 0], mode='L').save(tile_path)
                    elif tile_data.shape[2] == 3:  # RGB
                        Image.fromarray(tile_data[:, :, :3]).save(tile_path)
                    elif tile_data.shape[2] == 4:  # RGBA
                        Image.fromarray(tile_data[:, :, :4]).save(tile_path)
                    else:
                        print(f"Unexpected number of channels ({tile_data.shape[2]}) in {tile_path}")




tile_raster("/home/juju/lidar_mapping/athenee/hillshade_dsm.tif", "/home/juju/Bureau/test_tiling/", min_zoom=13, max_zoom=15, tile_size=256)

