import numpy as np
import numpy as np

def measure_smu(self, smu_num, vmeas, icomp=100e-3):
    """
    Performs a spot measurement on a single SMU.

    Parameters:
    - smu_num (int): SMU channel number
    - vmeas (float): Measurement voltage
    - icomp (float): Compliance current limit (default: 100mA)

    Returns:
    - data (str): Raw measurement data from B1500
    """
    smu_ch = self.smus[smu_num - 1]  # Get SMU channel

    # Set data format (ASCII output, comma-separated)
    self.b1500.write("FMT 1,1")  

    # Set number of averaging samples for measurement
    self.b1500.write("AV 10,1")  

    # Disable SMU filter (not always needed)
    self.b1500.write("FL 1")  

    # Select high-resolution ADC for precise measurement
    self.b1500.write(f"AAD {smu_ch},1")  

    # Enable timestamp recording for measurements
    self.b1500.write("TSC 1")  

    # Connect SMU channel before measurement
    self.b1500.write(f"CN {smu_ch}")  

    # Set voltage bias with compliance current
    self.b1500.write(f"MV {smu_ch},0,0,{vmeas},{icomp}")  

    # Set measurement mode to sampling
    self.b1500.write(f"MM 10,{smu_ch}")  

    # Set compliance mode (0: Compliance-side, 1: Current measurement)
    self.b1500.write(f"CMM {smu_ch},0")  

    # Read and return the measured data
    data = self.b1500.read()
    return data
