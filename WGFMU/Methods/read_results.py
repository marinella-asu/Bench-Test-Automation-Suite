import ctypes as ct  # Import C types for low-level interaction
import numpy as np  # Import NumPy for handling numerical data

def fetch_wgfmu_results(self, channel_id):
    """
    Retrieves measurement results from a specified WGFMU channel.

    Args:
        channel_id (int): The ID of the WGFMU channel to fetch results from.

    Returns:
        tuple: (timestamps, measured_values) as NumPy arrays.
    """
    num_points = ct.c_int()  # Create C integer for storing the number of data points
    self.wg.WGFMU_getMeasureValueSize(channel_id, ct.byref(num_points))  # Query number of data points

    if num_points.value == 0:  # If no data is available, return empty arrays
        return np.array([]), np.array([])

    # Create NumPy arrays to store results
    timestamps = np.zeros(num_points.value, dtype=np.float64)
    measured_values = np.zeros(num_points.value, dtype=np.float64)

    # Read measurement data
    self.wg.WGFMU_getMeasureValue(channel_id, timestamps.ctypes.data_as(ct.POINTER(ct.c_double)),
                                  measured_values.ctypes.data_as(ct.POINTER(ct.c_double)))

    return timestamps, measured_values  # Return the results as NumPy arrays
