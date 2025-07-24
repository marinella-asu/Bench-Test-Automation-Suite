def smu_meas_sample_multi_term(self, smu_numD, smu_numG, smu_numS, smu_numB, vmeasD, vmeasG, vmeasS, vmeasB, 
                               icompDSB, icompG, interval, pre_bias_time, number, 
                               disconnect_after=True, plot_results=False, activate_smus=True, clear_settings=True):
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
    self.b1500.write(f"AAD {smu_chD},1") #These are set to High Speed ADC For test but Change these to 1 to see if they'll auto revert to High speed during the Parallel measurement
    self.b1500.write(f"AAD {smu_chG},1") #REMEMBRE TO CHANGE THIS AND LOOK DURING FIRST TEST
    self.b1500.write(f"AAD {smu_chS},1")
    self.b1500.write(f"AAD {smu_chB},1")
    
    # Enable timestamps
    self.b1500.write( "TSC 1" )
    
    #Clear Timer Counter
    self.b1500.write( "TSR" )
    
    # Enable SMUs and set voltage bias
    if activate_smus:
        self.b1500.write(f"CN {smu_chD},{smu_chG},{smu_chS},{smu_chB}")  # Connect SMUs
    self.b1500.write(f"MV {smu_chD},0,0,{vmeasD},{icompDSB}")
    self.b1500.write(f"MV {smu_chG},0,0,{vmeasG},{icompG}")
    self.b1500.write(f"MV {smu_chS},0,0,{vmeasS},{icompDSB}")
    self.b1500.write(f"MV {smu_chB},0,0,{vmeasB},{icompDSB}")

    # Setup sampling measurement
    # self.b1500.write("PAD 1") #Enables parallel SMU measurements
    self.b1500.write(f"MT {pre_bias_time},{interval},{number}")  # Sampling time settings

    #just doing one measurement mode command on the gate SMU lets see what happens
    self.b1500.write(f"MM 10,{smu_chG}")  # Sampling measurement on Gate and Drain

    # Set current measurement mode
    self.b1500.write(f"CMM {smu_chG},1")
    self.b1500.write(f"CMM {smu_chD},1")
    self.b1500.write(f"CMM {smu_chS},1")
    self.b1500.write(f"CMM {smu_chB},1")

    # Execute measurement
    self.b1500.write("XE")
    self.b1500.query("*OPC?")
    
    # Read and process data
    # data = self.b1500.query("DO")  # Read measurement data from all SMUs
    data = self.b1500.read()
    
    # If clear_settings is True, remove biases but keep SMUs active
    if clear_settings:
        self.b1500.write(f"DZ {smu_chD}")  # Zero output to reset the voltage bias

    # Disconnect if required
    if disconnect_after:
        self.b1500.write(f"CL {smu_chG},{smu_chD},{smu_chS},{smu_chB}")


    # print(data)

    return data
