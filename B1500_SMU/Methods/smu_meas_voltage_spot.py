def smu_meas_voltage_spot( self, smu_num , imeas=0.0 , vcomp=10 , reset_timer=True, connect_first=True, disconnect_after=True ):
        # Performs a spot measurement and then disconnects and zeros all SMUs
        
        smu_ind = smu_num - 1
        smu_ch = self.smus[ smu_ind ] 
        self.b1500.write( "FMT 1,1")
        self.b1500.write( "AV 10,1" ) # Set number of averaging samples
        self.b1500.write( "FL 1" ) # Disable SMU Filter. Not sure if should be enabled or disabled
        self.b1500.write( f"AAD {smu_ch},1" ) # 0: fast ADC, 1: HR ADC
        
        # Connect SMUS
        #self.b1500.write( f"CN {smu_ch1},{smu_ch2},{smu_ch3},{smu_ch4}" )
        
        # Set Biases
        #self.b1500.write( f"DV {smu_ch1},0,0.0,100e-3" )
        #self.b1500.write( f"DV {smu_ch2},0,0.0,100e-3" )
        #self.b1500.write( f"DV {smu_ch3},0,3.3,100e-3" )
        #self.b1500.write( f"DV {smu_ch4},0,-3.3,100e-3" )
        
        # Bias IMEAS
        if connect_first:
            self.b1500.write( f"CN {smu_ch}" )
            self.b1500.write( f"DI {smu_ch},0,{imeas},{vcomp}" )
        
        # Reset timestamp and perform measurement
        if reset_timer:
            self.b1500.write( "TSR" ) # Resets timestamp for all SMU channels
        self.b1500.write( f"TTIV {smu_ch},0,0" ) # Performs high speed spot measurement and returns data and time 
        self.b1500.write( "TSQ" ) # returns time data from when the TSR command is sent until now
        
        if disconnect_after:
            self.b1500.write( f"CL {smu_ch}" )
        
        data = self.b1500.read()
        
        times , voltages , currents = self.process_data_str_tiv( data )
        
        return ( times , voltages , currents )