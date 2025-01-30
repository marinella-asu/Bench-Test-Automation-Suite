def smu_meas_sample_multi_parallel( self, smu_num0, vmeas0=0.1, icomp=100e-3, interval=10e-3, pre_bias_time=0, number=10, disconnect_after=True, plot_results=False, smu_num1 = 1, vmeas1=0.1, smu_num2 = 2, vmeas2=0.1, smu_num3 = 3, vmeas3=0.1):
        # applias DC bias to smu_num and performs repeated measurements on smu_num
        # interval: .1m to 65.535s. Default 2m
        # number max: 100001 / number of channels measured (lin) or 1 + (num that would give 11 decades) for log
        
        # Initial B1500 Measurement Setup
        smu_ind0 = smu_num0 - 1
        smu_ch0 = self.smus[ smu_ind0 ] 
        smu_ind1 = smu_num1 - 1
        smu_ch1 = self.smus[ smu_ind1 ] 
        smu_ind2 = smu_num2 - 1
        smu_ch2 = self.smus[ smu_ind2 ] 
        smu_ind3 = smu_num3 - 1
        smu_ch3 = self.smus[ smu_ind3 ] 
        self.b1500.write( "FMT 1,1")
        self.b1500.write( "AV 10,1" ) # Set number of averaging samples
        self.b1500.write( "FL 1" ) # Disable SMU Filter. Not sure if should be enabled or disabled
        ### 0: High speed ADC for high speed DC measurement, 1: High-resolution ADC for HR DC measurement, 2: High-speed ADC for pulsed-measurement
        self.b1500.write( f"AAD {smu_ch0},1" ) # 0: fast ADC, 1: HR ADC
        self.b1500.write( f"AAD {smu_ch1},1" ) # 0: fast ADC, 1: HR ADC
        self.b1500.write( f"AAD {smu_ch2},1" ) # 0: fast ADC, 1: HR ADC
        self.b1500.write( f"AAD {smu_ch3},1" ) # 0: fast ADC, 1: HR ADC


        # Enable timestamps
        self.b1500.write( "TSC 1" )
        
        # Bias VMEAS
        self.b1500.write( f"CN {smu_ch0}" )
        self.b1500.write( f"CN {smu_ch1}" )
        self.b1500.write( f"CN {smu_ch2}" )
        self.b1500.write( f"CN {smu_ch3}" )
        
        # Set up sampling measurement
        self.b1500.write( f"MV {smu_ch0},0,0,{vmeas0},{icomp}") # Bias settings
        self.b1500.write( f"MV {smu_ch1},0,0,{vmeas1},{icomp}") # Bias settings
        self.b1500.write( f"MV {smu_ch2},0,0,{vmeas2},{icomp}") # Bias settings
        self.b1500.write( f"MV {smu_ch3},0,0,{vmeas3},{icomp}") # Bias settings
        self.b1500.write( f"MT {pre_bias_time},{interval:.6E},{number}") # Sampling time settings
        self.b1500.write( f"MM 10,{smu_ch0}" ) # Measurement mode: sampling measurement on smu_ch
        self.b1500.write( f"MM 10,{smu_ch1}" ) # Measurement mode: sampling measurement on smu_ch
        self.b1500.write( f"MM 10,{smu_ch2}" ) # Measurement mode: sampling measurement on smu_ch
        self.b1500.write( f"MM 10,{smu_ch3}" ) # Measurement mode: sampling measurement on smu_ch
        self.b1500.write( f"CMM {smu_ch0},0" ) # 0: compliance side measurement, 1: current measurement
        self.b1500.write( f"CMM {smu_ch1},0" ) # 0: compliance side measurement, 1: current measurement
        self.b1500.write( f"CMM {smu_ch2},0" ) # 0: compliance side measurement, 1: current measurement
        self.b1500.write( f"CMM {smu_ch3},0" ) # 0: compliance side measurement, 1: current measurement

        # Reset timestamp and perform measurement
        self.b1500.write( "TSR" ) # Resets timestamp for all SMU channels
        self.b1500.write( "XE" ) # Execute measurement
        op_done = self.b1500.query( "*OPC?" ) # should block until operation completes
        
        # Clean up biases
        self.b1500.write( f"DZ {smu_ch0}" )
        self.b1500.write( f"DZ {smu_ch1}" )
        self.b1500.write( f"DZ {smu_ch2}" )
        self.b1500.write( f"DZ {smu_ch3}" )
        if disconnect_after:
            self.b1500.write( f"CL {smu_ch0}" )
            self.b1500.write( f"DZ {smu_ch1}" )
            self.b1500.write( f"DZ {smu_ch2}" )
            self.b1500.write( f"DZ {smu_ch3}" )
        
        # Read data
        data = self.b1500.read()
        
        # Process data
        # note that data order is different for sample measurement than for sweep/spot
        # sample_nums, currents, times = self.process_data_str_tiv( data )
        
        # plot_handles = ()
        # if plot_results:
        #     fig, ax = plt.subplots()
        #     ax.plot( times, currents , color='k', marker='o', ms=3, linestyle='-' )
        #     ax.set_xlabel( 'Time (s)', fontsize=14 )
        #     ax.set_ylabel( 'Current (A)', fontsize=14 )
            
        #     plot_handles = (fig, ax )
        
        return data