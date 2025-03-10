def smu_meas_sample_multi_term_int( self, smu_numD, smu_numG, smu_numS, smu_numB, vmeasD, vmeasG, vmeasS, vmeasB, icompDSB, icompG,  interval, pre_bias_time, number, disconnect_after=True, plot_results=False, int_num=6,activate_smus=True, clear_settings=True):
    # applias DC bias to smu_num and performs repeated measurements on smu_num
    # interval: .5m to 65.535s. Default 2m
    # number max: 100001 / number of channels measured (lin) or 1 + (num that would give 11 decades) for log
   
   
    # Initial B1500 Measurement Setup
    smu_indD = smu_numD - 1
    smu_chD = self.smus[ smu_indD ]
    smu_indS = smu_numS - 1
    smu_chS = self.smus[ smu_indS ]
    smu_indB = smu_numB - 1
    smu_chB = self.smus[ smu_indB ]
    smu_indG = smu_numG - 1
    smu_chG = self.smus[ smu_indG ]

    #orig below
    self.b1500.write( "FMT 1,1")
    #self.b1500.write("FMT 3,1")
    self.b1500.write( "AV 1,1" ) # Set number of averaging samples
    self.b1500.write( "FL 1" ) # Disable SMU Filter. Not sure if should be enabled or disabled


    #originally 1
    self.b1500.write(f"AAD {smu_chD},0") #These are set to High Speed ADC For test but Change these to 1 to see if they'll auto revert to High speed during the Parallel measurement
    self.b1500.write(f"AAD {smu_chG},0") #REMEMBRE TO CHANGE THIS AND LOOK DURING FIRST TEST
    self.b1500.write(f"AAD {smu_chS},0")
    self.b1500.write(f"AAD {smu_chB},0")

    # Enable timestamps
    self.b1500.write( "TSC 1" )
    
    #Clear Timer Counter
    self.b1500.write( "TSR" )
    #Integration Time control
    self.b1500.write( f"AIT 1,1,{int_num}" ) # type, mode, (integration number/time): 1-High Resolution; mode 0-default 1-manual 2-PWL 3-Time-dependent; N: integration number or time(only for mode 3)
    
    #Compliance Current Control
    # self.b1500.write( f"RI {sum_num},1,{}")
    
    # Enable SMUs and set voltage bias
    if activate_smus:
        self.b1500.write(f"CN {smu_chD},{smu_chG},{smu_chS},{smu_chB}")  # Connect SMUs
    self.b1500.write(f"MV {smu_chD},0,0,{vmeasD},{icompDSB}")
    self.b1500.write(f"MV {smu_chG},0,0,{vmeasG},{icompG}")
    self.b1500.write(f"MV {smu_chS},0,0,{vmeasS},{icompDSB}")
    self.b1500.write(f"MV {smu_chB},0,0,{vmeasB},{icompDSB}")

    #orig below
    #self.b1500.write( f"MT {pre_bias_time},{interval:.6E},{number}") # Sampling time settings
    # self.b1500.write( f"MT {pre_bias_time},{interval},{number}") # Sampling time settings

    #all simultaneously note this drastically increase the pulse duration probaply factor of 2x
    #self.b1500.write( f"MM 10,{smu_chD},{smu_chG},{smu_chS},{smu_chB}" ) # Measurement mode: sampling measurement on smu_ch
    
    #all individually should lead to the lowest pulse
    #self.b1500.write( f"MM 10,{smu_chD}" ) # Measurement mode: sampling measurement on smu_ch
    #self.b1500.write( f"MM 10,{smu_chG}" ) # Measurement mode: sampling measurement on smu_ch
    #self.b1500.write( f"MM 10,{smu_chS}" ) # Measurement mode: sampling measurement on smu_ch
    #self.b1500.write( f"MM 10,{smu_chB}" ) # Measurement mode: sampling measurement on smu_ch

    self.b1500.write("PAD 1") #Enables parallel SMU measurements
    self.b1500.write(f"MT {pre_bias_time},{interval},{number}")  # Sampling time settings

    #just doing one measurement mode command on the gate SMU lets see what happens
    self.b1500.write(f"MM 10,{smu_chG}, {smu_chD}")  # Sampling measurement on Gate and Drain
    
    #originally compliance mode set to 0 now measurement
    self.b1500.write( f"CMM {smu_chG},1" ) # 0: compliance side measurement, 1: current measurement
    self.b1500.write( f"CMM {smu_chD},1" ) # 0: compliance side measurement, 1: current measurement
    self.b1500.write( f"CMM {smu_chS},1" ) # 0: compliance side measurement, 1: current measurement
    self.b1500.write( f"CMM {smu_chB},1" ) # 0: compliance side measurement, 1: current measurement
    
    # Reset timestamp and perform measurement
    #self.b1500.write( "TSR" ) # Resets timestamp for all SMU channels
    self.b1500.write( "XE" ) # Execute measurement
    op_done = self.b1500.query( "*OPC?" ) # should block until operation completes
    
    # If clear_settings is True, remove biases but keep SMUs active
    if clear_settings:
        self.b1500.write(f"DZ {smu_chD}")  # Zero output to reset the voltage bias

    # Disconnect if required
    if disconnect_after:
        self.b1500.write(f"CL {smu_chG},{smu_chD},{smu_chS},{smu_chB}")
    
    # Read data
    data = self.b1500.read()

    return(data)