def bias_smu_rd(self, smu_num, voltage, num_averaging_samples, Icomp=100e-3):
    """
    Applies a voltage bias to an SMU and performs a measurement.
    
    Parameters:
    - smu_num (int): SMU channel number
    - voltage (float): Voltage to apply
    - num_averaging_samples (int): Number of averaging samples
    - Icomp (float): Compliance current limit (default: 100mA)

    Returns:
    - times (numpy array): Time data points
    - voltage (numpy array): Measured voltage
    - current (numpy array): Measured current
    """
    smu_ch = self.smus[smu_num - 1]

    # Apply bias voltage
    self.b1500.write(f"DV {smu_ch},0,{voltage},{Icomp:.3E}")

    # Measurement settings
    self.b1500.write("FMT 1,1")
    self.b1500.write("TSC 1")  # Enable timestamp output
    self.b1500.write("FL 1")   # Disable SMU filter
    self.b1500.write(f"AV {num_averaging_samples},0")  # Set averaging samples
    self.b1500.write(f"AAD {smu_ch},1")  # HR ADC

    # Set up sweep measurement
    self.b1500.write(f"MM 2,{smu_ch}")  # Staircase sweep
    self.b1500.write(f"CMM {smu_ch},0")  # Compliance-side measurement
    self.b1500.write(f"RI {smu_ch},11")  # Auto-ranging

    # Reset timestamp and execute measurement
    self.b1500.write("TSR")
    self.b1500.write("XE")

    # Wait for operation to complete
    self.b1500.query("*OPC?")

    # Read and process data
    data = self.b1500.read()
    times, voltage, current = self.process_data_str_tiv(data)
    
    return times, voltage, current
