def smu_meas_spot_rpt(self, smu_num, vmeas=0.1, icomp=100e-3, meas_pts=1, meas_interval=0, reset_timer=True, disconnect_after=True):
    """
    Repeatedly performs spot measurements on a specified SMU.

    Parameters:
    - smu_num (int): SMU channel number
    - vmeas (float): Measurement voltage (default: 0.1V)
    - icomp (float): Compliance current limit (default: 100mA)
    - meas_pts (int): Number of measurement points
    - meas_interval (float): Time interval between measurements
    - reset_timer (bool): Reset timestamp before measurement (default: True)
    - disconnect_after (bool): Disconnect SMU after measurement (default: True)

    Returns:
    - times (numpy array): Time data points
    - voltages (numpy array): Measured voltages
    - currents (numpy array): Measured currents
    """
    smu_ch = self.smus[smu_num - 1]

    # Setup measurement
    self.b1500.write("FMT 1,1")
    self.b1500.write("AV 10,1")  # Set averaging samples
    self.b1500.write("FL 1")  # Disable SMU filter
    self.b1500.write(f"AAD {smu_ch},1")  # HR ADC

    # Apply voltage bias
    self.b1500.write(f"CN {smu_ch}")
    self.b1500.write(f"DV {smu_ch},0,{vmeas},{icomp}")

    # Reset timestamp if required
    if reset_timer:
        self.b1500.write("TSR")

    # Perform repeated measurements
    for _ in range(meas_pts):
        self.b1500.write(f"TTIV {smu_ch},11,0")  # Spot measurement
        time.sleep(meas_interval)

    # Disconnect if required
    if disconnect_after:
        self.b1500.write(f"CL {smu_ch}")

    # Process multiple measurement data
    num_meas = int(self.get_number_of_measurements() / 3)  # Time, Voltage, Current
    times = np.zeros(num_meas)
    voltages = np.zeros(num_meas)
    currents = np.zeros(num_meas)

    for i in range(num_meas):
        data = self.b1500.read()
        tt, vv, ii = self.process_data_str_tiv(data)
        times[i] = tt
        voltages[i] = vv
        currents[i] = ii

    return times, voltages, currents
