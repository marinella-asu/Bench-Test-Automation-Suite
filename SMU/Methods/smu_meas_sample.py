import numpy as np
import matplotlib.pyplot as plt

def smu_meas_sample(self, smu_num, vmeas=0.1, icomp=100e-3, interval=10e-3, pre_bias_time=0, number=10, disconnect_after=True, plot_results=False):
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
    self.b1500.write("FMT 1,1")  

    # Configure number of averaging samples
    self.b1500.write("AV 10,1")  

    # Disable SMU filter
    self.b1500.write("FL 1")  

    # Select high-resolution ADC
    self.b1500.write(f"AAD {smu_ch},1")  

    # Enable timestamp output
    self.b1500.write("TSC 1")  

    # Connect SMU
    self.b1500.write(f"CN {smu_ch}")  

    # Apply voltage bias
    self.b1500.write(f"MV {smu_ch},0,0,{vmeas},{icomp}")  

    # Configure sampling measurement
    self.b1500.write(f"MT {pre_bias_time},{interval:.6E},{number}")  

    # Set measurement mode to sampling
    self.b1500.write(f"MM 10,{smu_ch}")  

    # Set compliance mode
    self.b1500.write(f"CMM {smu_ch},1")  

    # Reset timestamp before starting measurement
    self.b1500.write("TSR")  

    # Execute measurement
    self.b1500.write("XE")  
    self.b1500.query("*OPC?")  

    # Zero SMU output after measurement
    self.b1500.write(f"DZ {smu_ch}")  

    # Disconnect SMU if required
    if disconnect_after:
        self.b1500.write(f"CL {smu_ch}")  

    # Read and process data
    data = self.b1500.read()
    times, currents, _ = self.process_data_str_tiv(data)

    # Plot results if enabled
    plot_handles = ()
    if plot_results:
        fig, ax = plt.subplots()
        ax.plot(times, currents, color='k', marker='o', ms=3, linestyle='-')
        ax.set_xlabel('Time (s)', fontsize=14)
        ax.set_ylabel('Current (A)', fontsize=14)
        plot_handles = (fig, ax)

    return times, currents, plot_handles
