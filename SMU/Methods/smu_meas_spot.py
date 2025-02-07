def smu_meas_spot(self, smu_num, vmeas=0.1, icomp=100e-3, reset_timer=True, disconnect_after=True):
    """
    Performs a spot measurement on a specified SMU.

    Parameters:
    - smu_num (int): SMU channel number
    - vmeas (float): Measurement voltage (default: 0.1V)
    - icomp (float): Compliance current limit (default: 100mA)
    - reset_timer (bool): Reset timestamp before measurement (default: True)
    - disconnect_after (bool): Disconnect SMU after measurement (default: True)

    Returns:
    - times (numpy array): Time data points
    - voltages (numpy array): Measured voltages
    - currents (numpy array): Measured currents
    """
    smu_ch = self.smus[smu_num - 1]

    # Measurement settings
    self.b1500.write("FMT 1,1")
    self.b1500.write("AV 10,1")  # Set averaging samples
    self.b1500.write("FL 1")  # Disable SMU filter
    self.b1500.write(f"AAD {smu_ch},1")  # HR ADC

    # Apply voltage bias
    self.b1500.write(f"CN {smu_ch}")  # Connect SMU
    self.b1500.write(f"DV {smu_ch},0,{vmeas},{icomp}")  # Apply bias

    # Reset timestamp if required
    if reset_timer:
        self.b1500.write("TSR")

    # Perform measurement
    self.b1500.write(f"TTIV {smu_ch},0,0")
    self.b1500.write("TSQ")  # Get timestamp

    # Disconnect if required
    if disconnect_after:
        self.b1500.write(f"CL {smu_ch}")

    # Read and process data
    data = self.b1500.read()
    times, voltages, currents = self.process_data_str_tiv(data)
    
    return times, voltages, currents
