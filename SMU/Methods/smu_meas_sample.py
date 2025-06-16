import numpy as np
import matplotlib.pyplot as plt

def smu_meas_sample(self, b1500, smu_num, vmeas=0.1, icomp=100e-3, interval=10e-3, pre_bias_time=0, number=1, disconnect_after=True):
    """
    Applies a DC bias to an SMU and performs repeated measurements.

    Parameters:
    - smu_num (int): SMU channel number
    - vmeas (float): Bias voltage
    - icomp (float): Compliance current
    - interval (float): Time interval between measurements (0.1ms to 65.535s)
    - pre_bias_time (float): Time before measurement starts
    - number (int): Number of measurement points
    - disconnect_after (bool): Disconnect SMU after measurement
    - plot_results (bool): Plot results if True

    Returns:
    - times (numpy array): Time data
    - currents (numpy array): Current data
    - plot_handles (tuple): Handles for plots (if enabled)
    """
    smu_ch = self.smus[smu_num - 1]  # Assign SMU channel

    # Set measurement format
    b1500.connection.write("FMT 1,1")  

    # Configure number of averaging samples
    b1500.connection.write("AV 10,1")  

    # Disable SMU filter
    b1500.connection.write("FL 1")  

    # Select high-resolution ADC
    b1500.connection.write(f"AAD {smu_ch},1")  

    # Enable timestamp output
    b1500.connection.write("TSC 1")  

    # Connect SMU
    b1500.connection.write(f"CN {smu_ch}")  

    # Apply voltage bias
    b1500.connection.write(f"MV {smu_ch},0,0,{vmeas},{icomp}")  

    # Configure sampling measurement
    b1500.connection.write(f"MT {pre_bias_time},{interval:.6E},{number}")  

    # Set measurement mode to sampling
    b1500.connection.write(f"MM 10,{smu_ch}")  

    # Set compliance mode
    b1500.connection.write(f"CMM {smu_ch},1")  

    # Reset timestamp before starting measurement
    b1500.connection.write("TSR")  

    # Execute measurement
    b1500.connection.write("XE")  
    b1500.connection.query("*OPC?")  

    # Zero SMU output after measurement
    b1500.connection.write(f"DZ {smu_ch}")  

    return b1500.connection.read()

    # Disconnect SMU if required
    if disconnect_after:
        b1500.connection.write(f"CL {smu_ch}")  
