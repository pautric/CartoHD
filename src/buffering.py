import subprocess
import numpy as np
import rasterio
from scipy.ndimage import binary_dilation

import numpy as np
import rasterio
from scipy.ndimage import binary_dilation, binary_erosion


def run_command(command):
    result = subprocess.run(command, capture_output=True, text=True)
    print(result.stdout)
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
    # Open the TIFF file
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


