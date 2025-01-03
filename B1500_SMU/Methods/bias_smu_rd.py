def bias_smu_rd( self , smu_num , voltage,num_averaging_samples, Icomp=100e-3):
        # Use Keysight SMU numbering. Starts at 1
        smu_ch = self.smus[ smu_num - 1 ]
        #connect = f"CN {smu_ch}"
        bias = f"DV {smu_ch},0,{voltage},{Icomp:.3E}"
        #b1500.write( connect )
        self.b1500.write( bias )   
        
        self.b1500.write( "FMT 1,1" )
        self.b1500.write( "TSC 1" ) # enable timestamp output
        self.b1500.write( "FL 1" ) # 0: disable smu filter, 1: enable
        self.b1500.write( f"AV {num_averaging_samples},0" ) # Sets averaging (10 samples to 1 data point)
        self.b1500.write( f"AD {smu_ch},0" ) # fast ADC
        self.b1500.write( f"AAD {smu_ch},1" ) # 0: fast ADC, 1: HR ADC
        
        # Connect SMUS
#        if connect_first:
#           self.b1500.write( f"CN {smu_ch}" ) # connect sweep SMU
#           self.b1500.write( f"DV {smu_ch},0,{vstart}" ) # set sweep SMU to start voltage pre-emptively
                                                          #    ch,range_setting,voltage. leave range setting at 0 for auto.
        # Sweep setup
        self.b1500.write( f"MM 2,{smu_ch}" ) # Staircase sweep measurement on SMU1
        self.b1500.write( f"CMM {smu_ch},0" ) # 0: compliance side measurement, 1: current measurement
        self.b1500.write( f"RI {smu_ch},11" ) # 0: auto ranging # 11 - 1nA Limited (matches EasyExpert)
#        self.b1500.write( f"WT 0,0,0" ) # hold, delay, s_delay to 0
        self.b1500.write( f"WM 1,1" ) # A,B - A =1 keep going if we hit compliance, A=2 abort if we hit compliance, B=1 = return to START val after meas, B=2 =stay at STOP val after meas
        
        # WV Command
        # WV chnum,mode,range,start,stop,step[,Icomp[,Pcomp]]
        # mode: 1 - Linear,  2 - Log, 3: Linear bidirectional, 4: Log bidirectional
#        self.b1500.write( f"WV {smu_ch},{mode},0,{vstart},{vstop},{nsteps},{icomp:.2E}")
        self.b1500.write( "TSR" ) # Reset timestamp for all channels
        
        self.b1500.write( "XE" ) # Execute measurement
        
        op_done = self.b1500.query( "*OPC?" ) # should block until operation completes, I think
        #print( f"OP_DONE: {op_done.strip()}" )
        
        
        # Reset Measurement SMU
#        if disconnect_after:
#            self.b1500.write( f"CL {smu_ch}" ) # Disconnect sweep SMU
        
        # Read data
        
        data = self.b1500.read()
    
        # Process data
        times , voltage , current = self.process_data_str_tiv( data )
            
        return times, voltage, current 