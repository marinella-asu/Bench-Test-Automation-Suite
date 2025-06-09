import ctypes as ct  # Import C types for low-level interaction
import numpy as np  # Import NumPy for handling numerical data

def read_results(self, channel_id):
    """
    Retrieves measurement results from a specified WGFMU channel.

    Args:
        channel_id (int): The ID of the WGFMU channel to fetch results from.

    Returns:
        tuple: (timestamps, measured_values) as NumPy arrays.
    """
    num_points = ct.c_int()  # Create C integer for storing the number of data points
    total_size = ct.c_int()
    self.wg.WGFMU_getMeasureValueSize(channel_id, ct.byref( num_points ), ct.byref( total_size ) )  # Query number of data points
    # print(num_points)
    times = np.zeros( num_points.value )
    values = np.zeros( num_points.value )
        
    for ind in range( 0, num_points.value ):
        time = ct.c_double()
        value = ct.c_double()
        #voltage = ct.c_double()
        
        self.wg.WGFMU_getMeasureValue( channel_id , ind , ct.byref( time ) , ct.byref( value ) )
        #wg.WGFMU_getInterpolatedForceValue( channel_id1 , time , ct.byref( voltage ) )
        #print(f"This is channel_id: {channel_id}") #Quinn
        #print(f"This is time: {time}") #Quinn
        #print(f"This is value: {value}") #Quinn
        times[ind] = time.value
        values[ind] = value.value

    return times, values  # Return the results as NumPy arrays
