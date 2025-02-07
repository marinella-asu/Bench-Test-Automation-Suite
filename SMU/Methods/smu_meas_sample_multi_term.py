def smu_meas_sample_multi_term(self, smu_numD, smu_numG, smu_numS, smu_numB, vmeasD, vmeasG, vmeasS, vmeasB, 
                               icompDSB, icompG, interval, pre_bias_time, number, 
                               disconnect_after=True, plot_results=False):
    """
    Applies DC bias to multiple SMUs and performs repeated measurements.

    Parameters:
    - smu_numD, smu_numG, smu_numS, smu_numB (int): SMU channel numbers for Drain, Gate, Source, and Bulk
    - vmeasD, vmeasG, vmeasS, vmeasB (float): Bias voltages for each terminal
    - icompDSB, icompG (float): Compliance currents
    - interval (float): Sampling interval (0.1ms to 65.535s)
    - pre_bias_time (float): Time before measurement starts
    - number (int): Number of measurement points
    - disconnect_after (bool): Disconnect SMUs after measurement (default: True)
    - plot_results (bool): Plot results if True

    Returns:
    - Raw measurement data
    """
    smu_chD = self.smus[smu_numD - 1]
    smu_chG = self.smus[smu_numG - 1]
    smu_chS = self.smus[smu_numS - 1]
    smu_chB = self.smus[smu_numB - 1]

    # Configure measurement settings
    self.b1500.write("FMT 1,1")
    self.b1500.write("AV 1,1")  # Set averaging samples
    self.b1500.write("FL 1")  # Disable SMU filter
    self.b1500.write(f"AAD {smu_chD},1")
    self.b1500.write(f"AAD {smu_chG},1")
    self.b1500.write(f"AAD {smu_chS},1")
    self.b1500.write(f"AAD {smu_chB},1")

    # Enable SMUs and set voltage bias
    self.b1500.write(f"CN {smu_chD},{smu_chG},{smu_chS},{smu_chB}")
    self.b1500.write(f"MV {smu_chD},0,0,{vmeasD},{icompDSB}")
    self.b1500.write(f"MV {smu_chG},0,0,{vmeasG},{icompG}")
    self.b1500.write(f"MV {smu_chS},0,0,{vmeasS},{icompDSB}")
    self.b1500.write(f"MV {smu_chB},0,0,{vmeasB},{icompDSB}")

    # Setup sampling measurement
    self.b1500.write(f"MT {pre_bias_time},{interval},{number}")
    self.b1500.write(f"MM 10,{smu_chG}")  # Sampling measurement on Gate

    # Set current measurement mode
    self.b1500.write(f"CMM {smu_chG},1")
    self.b1500.write(f"CMM {smu_chD},1")
    self.b1500.write(f"CMM {smu_chS},1")
    self.b1500.write(f"CMM {smu_chB},1")

    # Execute measurement
    self.b1500.write("XE")
    self.b1500.query("*OPC?")

    # Disconnect if required
    if disconnect_after:
        self.b1500.write(f"CL {smu_chG},{smu_chD},{smu_chS},{smu_chB}")

    # Read and process data
    data = self.b1500.read()
    print(data)

    return data
