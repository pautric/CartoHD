import numpy as np
import rasterio
from scipy.ndimage import binary_dilation

def buffer_tiff(input_path, output_path, buffer_distance):
    """
    Buffers pixels with value 1 in a TIFF image.

    Parameters:
        input_path (str): Path to the input TIFF file.
        output_path (str): Path to save the output buffered TIFF file.
        buffer_distance (int): Number of pixels to buffer around each pixel with value 1.
    """
    # Open the TIFF file
    with rasterio.open(input_path) as src:
        data = src.read(1)  # Read the first band
        no_data_value = src.nodata
        
        if no_data_value is None:
            raise ValueError("Input TIFF file does not specify a 'no_data' value.")

        # Create a mask of pixels with value 1
        valid_data_mask = data == 1

        # Generate a structuring element for dilation based on the buffer distance
        structure = np.ones((2 * buffer_distance + 1, 2 * buffer_distance + 1))

        # Apply a binary dilation to buffer the pixels
        buffered_mask = binary_dilation(valid_data_mask, structure=structure)

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

    print(f"Buffered TIFF saved to: {output_path}")
