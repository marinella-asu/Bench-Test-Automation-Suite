def smu_meas_voltage_spot(self, smu_num, imeas=0.0, vcomp=10, reset_timer=True, connect_first=True, disconnect_after=True):
    """
    Performs a spot voltage measurement by applying a current and measuring voltage.

    Parameters:
    - smu_num (int): SMU channel number
    - imeas (float): Current applied for measurement (default: 0.0A)
    - vcomp (float): Compliance voltage (default: 10V)
    - reset_timer (bool): Reset timestamp before measurement (default: True)
    - connect_first (bool): Connect SMU before measurement (default: True)
    - disconnect_after (bool): Disconnect SMU after measurement (default: True)

    Returns:
    - times, voltages, currents (numpy arrays)
    """
    smu_ch = self.smus[smu_num - 1]  # Get SMU channel

    # Set data output format (ASCII, with headers)
    self.b1500.write("FMT 1,1")

    # Set number of averaging samples (10 samples per point)
    self.b1500.write("AV 10,1")

    # Disable SMU filter (ensures raw measurements without filtering)
    self.b1500.write("FL 1")

    # Use high-resolution ADC for accurate measurements
    self.b1500.write(f"AAD {smu_ch},1")

    # Connect SMU if required
    if connect_first:
        self.b1500.write(f"CN {smu_ch}")  # Connect the SMU

        # Apply current source with voltage compliance
        self.b1500.write(f"DI {smu_ch},0,{imeas},{vcomp}")

    # Reset timestamp before measurement (if enabled)
    if reset_timer:
        self.b1500.write("TSR")

    # Perform high-speed spot measurement (returns time, voltage, and current)
    self.b1500.write(f"TTIV {smu_ch},0,0")

    # Query timestamp after measurement
    self.b1500.write("TSQ")

    # Disconnect SMU after measurement (if enabled)
    if disconnect_after:
        self.b1500.write(f"CL {smu_ch}")

    # Read and process measurement data
    data = self.b1500.read()
    return self.process_data_str_tiv(data)
