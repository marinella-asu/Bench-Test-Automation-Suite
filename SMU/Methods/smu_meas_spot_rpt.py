def smu_meas_spot_rpt(self, smu_num, vmeas=0.1, icomp=100e-3, meas_pts=1, meas_interval=0, reset_timer=True, disconnect_after=True ):
        #biases device and measures continuously
        smu_ind = smu_num - 1
        smu_ch = self.smus[ smu_ind ] 
        self.b1500.write( "FMT 1,1")
        self.b1500.write( "AV 10,1" ) # Set number of averaging samples
        self.b1500.write( "FL 1" ) # Disable SMU Filter. Not sure if should be enabled or disabled
        self.b1500.write( f"AAD {smu_ch},1" ) # 0: fast ADC, 1: HR ADC
        
        # Bias VMEAS
        self.b1500.write( f"CN {smu_ch}" )
        self.b1500.write( f"DV {smu_ch},0,{vmeas},{icomp}" )
        
        # Reset timestamp and perform measurement
        if reset_timer:
            self.b1500.write( "TSR" ) # Resets timestamp for all SMU channels
        
        for ii in range(meas_pts):
            self.b1500.write( f"TTIV {smu_ch},11,0" ) # Performs high speed spot measurement and returns data and time
            time.sleep(meas_interval)
        #self.b1500.write( "TSQ" ) # returns time data from when the TSR command is sent until now
        
        self.b1500.write( f"DZ {smu_ch}" )
        if disconnect_after:
            self.b1500.write( f"CL {smu_ch}" )
        
        num_meas = int(self.get_number_of_measurements()/3) # three we get time, current, voltage back
        times = np.zeros(num_meas)
        voltages = np.zeros(num_meas)
        currents = np.zeros(num_meas)
        for mm in range(num_meas):
            data = self.b1500.read()
            tt, vv, ii = self.process_data_str_tiv( data )
            times[mm] = tt
            voltages[mm] = vv
            currents[mm] = ii
        
        return ( times , voltages , currents )