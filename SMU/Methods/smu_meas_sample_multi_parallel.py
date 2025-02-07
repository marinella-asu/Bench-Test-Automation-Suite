import numpy as np

def smu_meas_sample_multi_parallel(self, smu_num0, vmeas0=0.1, icomp=100e-3, interval=10e-3, 
                                   pre_bias_time=0, number=10, disconnect_after=True, 
                                   plot_results=False, smu_num1=1, vmeas1=0.1, 
                                   smu_num2=2, vmeas2=0.1, smu_num3=3, vmeas3=0.1):
    """
    Applies DC bias to multiple SMUs and performs repeated measurements in parallel.

    Parameters:
    - smu_num0, smu_num1, smu_num2, smu_num3 (int): SMU channel numbers
    - vmeas0, vmeas1, vmeas2, vmeas3 (float): Bias voltages
    - icomp (float): Compliance current
    - interval (float): Time interval between measurements (0.1ms to 65.535s)
    - pre_bias_time (float): Time before measurement starts
    - number (int): Number of measurement points
    - disconnect_after (bool): Disconnect SMUs after measurement
    - plot_results (bool): Plot results if True

    Returns:
    - data (str): Raw measurement data from B1500
    """
    smu_ch0 = self.smus[smu_num0 - 1]
    smu_ch1 = self.smus[smu_num1 - 1]
    smu_ch2 = self.smus[smu_num2 - 1]
    smu_ch3 = self.smus[smu_num3 - 1]

    # Set measurement format
    self.b1500.write("FMT 1,1")  

    # Configure number of averaging samples
    self.b1500.write("AV 10,1")  

    # Disable SMU filter
    self.b1500.write("FL 1")  

    # Select high-resolution ADC for each SMU
    self.b1500.write(f"AAD {smu_ch0},1")  
    self.b1500.write(f"AAD {smu_ch1},1")  
    self.b1500.write(f"AAD {smu_ch2},1")  
    self.b1500.write(f"AAD {smu_ch3},1")  

    # Enable timestamp output
    self.b1500.write("TSC 1")  

    # Connect SMUs
    self.b1500.write(f"CN {smu_ch0},{smu_ch1},{smu_ch2},{smu_ch3}")  

    # Apply voltage biases
    self.b1500.write(f"MV {smu_ch0},0,0,{vmeas0},{icomp}")  
    self.b1500.write(f"MV {smu_ch1},0,0,{vmeas1},{icomp}")  
    self.b1500.write(f"MV {smu_ch2},0,0,{vmeas2},{icomp}")  
    self.b1500.write(f"MV {smu_ch3},0,0,{vmeas3},{icomp}")  

    # Configure sampling measurement timing
    self.b1500.write(f"MT {pre_bias_time},{interval:.6E},{number}")  

    # Set measurement mode to sampling for all SMUs
    self.b1500.write(f"MM 10,{smu_ch0}")  
    self.b1500.write(f"MM 10,{smu_ch1}")  
    self.b1500.write(f"MM 10,{smu_ch2}")  
    self.b1500.write(f"MM 10,{smu_ch3}")  

    # Set compliance mode (0: Compliance-side measurement)
    self.b1500.write(f"CMM {smu_ch0},0")  
    self.b1500.write(f"CMM {smu_ch1},0")  
    self.b1500.write(f"CMM {smu_ch2},0")  
    self.b1500.write(f"CMM {smu_ch3},0")  

    # Reset timestamp before measurement
    self.b1500.write("TSR")  

    # Execute measurement
    self.b1500.write("XE")  
    self.b1500.query("*OPC?")  

    # Zero SMU outputs after measurement
    self.b1500.write(f"DZ {smu_ch0}")  
    self.b1500.write(f"DZ {smu_ch1}")  
    self.b1500.write(f"DZ {smu_ch2}")  
    self.b1500.write(f"DZ {smu_ch3}")  

    # Disconnect SMUs if required
    if disconnect_after:
        self.b1500.write(f"CL {smu_ch0},{smu_ch1},{smu_ch2},{smu_ch3}")  

    # Read and return the measurement data
    data = self.b1500.read()
    return data
