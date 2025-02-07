def multichan_pulsed_spot(self, smu_numD, smu_numG, smu_numS, smu_numB, vmeasDSB, vmeasG, icompDSB, icompG, interval, pre_bias_time, number, disconnect_after=True, plot_results=False):
    """
    Performs a multi-channel pulsed spot measurement.

    Parameters:
    - smu_numD, smu_numG, smu_numS, smu_numB (int): SMU channels for Drain, Gate, Source, Bulk
    - vmeasDSB, vmeasG (float): Bias voltages
    - icompDSB, icompG (float): Compliance current limits
    - interval (float): Measurement interval
    - pre_bias_time (float): Pre-bias time before measurement
    - number (int): Number of measurements
    - disconnect_after (bool): Disconnect SMUs after measurement
    - plot_results (bool): Plot results if True

    Returns:
    - None (prints data)
    """
    # Assign SMU channels
    smu_chD = self.smus[smu_numD - 1]
    smu_chG = self.smus[smu_numG - 1]
    smu_chS = self.smus[smu_numS - 1]
    smu_chB = self.smus[smu_numB - 1]

    # Set data format (Binary output for faster data processing)
    self.b1500.write("FMT 3,1")  

    # Disable SMU filter
    self.b1500.write("FL 0")  

    # Enable timestamp recording
    self.b1500.write("TSC 1")  

    # Connect all SMU channels
    self.b1500.write(f"CN {smu_chD},{smu_chG},{smu_chS},{smu_chB}")  

    # Set ADC measurement timing (pulsed measurement mode)
    self.b1500.write("AIT 2,3,0.000001")  

    # Configure pulsed measurement timing (hold time, pulse period, averaging)
    self.b1500.write("MCPT 0,0.00005,0,1")  

    # Set measurement channels for pulsed spot mode (MM27)
    self.b1500.write(f"MM 27,{smu_chD},{smu_chG},{smu_chS},{smu_chB}")  

    # Apply bias voltages
    self.b1500.write(f"DV {smu_chD},0,{vmeasDSB},{icompDSB}")  
    self.b1500.write(f"DV {smu_chG},0,{vmeasG},{icompG}")  
    self.b1500.write(f"DV {smu_chS},0,{vmeasDSB},{icompDSB}")  
    self.b1500.write(f"DV {smu_chB},0,{vmeasDSB},{icompDSB}")  

    # Set compliance mode for each channel (0: Compliance-side measurement)
    self.b1500.write(f"CMM {smu_chD},0")  
    self.b1500.write(f"CMM {smu_chG},0")  
    self.b1500.write(f"CMM {smu_chS},0")  
    self.b1500.write(f"CMM {smu_chB},0")  

    # Enable auto-ranging for current measurement
    self.b1500.write(f"RI {smu_chD},0")  
    self.b1500.write(f"RI {smu_chG},0")  
    self.b1500.write(f"RI {smu_chS},0")  
    self.b1500.write(f"RI {smu_chB},0")  

    # Reset timestamp before measurement
    self.b1500.write("TSR")  

    # Execute measurement
    self.b1500.write("XE")  
    self.b1500.query("*OPC?")  

    # Disconnect SMUs if required
    if disconnect_after:
        self.b1500.write(f"CL {smu_chD},{smu_chG},{smu_chS},{smu_chB}")  
