def smu_meas_sweep_wdrainmeas( self , smu_num ,smudchan, smudrain_bias, vstart=0.0 , vstop=0.10 , nsteps=51 , mode=1, icomp=100e-3, num_averaging_samples=1 , connect_first=True, disconnect_after=True , vmax_override=False, plot_data=False):
        # Connects smu_num and performs a measurement sweep with minimum hold/delay settings
        # MODE: 1 = linear, 2 = log , 3 = linear bidirectional , 4 = log bidirectional
        # Max steps = 10001
        VMAX = 7
        if ((np.abs(vstart) > VMAX) or (np.abs(vstop) > VMAX)) and (not vmax_override):
            raise ValueError("Chosen voltage range is ABOVE 7V! If you really want to do this, set vmax_override=True" )
        smu_ind = smu_num - 1
        smu_ch = self.smus[ smu_ind ]

        #adding drain channel connection
        smu_indDrain = smudchan - 1
        smu_ch_drain = self.smus[smu_indDrain]
        
        self.b1500.write( "FMT 1,1" )
        self.b1500.write( "TSC 1" ) # enable timestamp output
        self.b1500.write( "FL 1" ) # 0: disable smu filter, 1: enable
        self.b1500.write( f"AV {num_averaging_samples},0" ) # Sets averaging (10 samples to 1 data point)
        #self.b1500.write( f"AD {smu_ch},0" ) # fast ADC
        ##skips below AAD command in programming guide 
        self.b1500.write( f"AAD {smu_ch},1" ) # 0: fast ADC, 1: HR ADC
        self.b1500.write( f"AAD {smu_ch_drain},1" ) # 0: fast ADC, 1: HR ADC
        # Connect SMUS
        if connect_first:
            self.b1500.write( f"CN {smu_ch_drain}" ) # connect drain measure SMU
            self.b1500.write( f"DV {smu_ch_drain},0,{smudrain_bias}" ) # set sweep SMU to start voltage pre-emptively
            self.b1500.write( f"CN {smu_ch}" ) # connect sweep SMU
            self.b1500.write( f"DV {smu_ch},0,{vstart}" ) # set sweep SMU to start voltage pre-emptively
                                                            #    ch,range_setting,voltage. leave range setting at 0 for auto.
        #drain measurement_setup
        self.b1500.write( f"CMM {smu_ch_drain},1" ) # 0: compliance side measurement, 1: current measurement
        self.b1500.write( f"RI {smu_ch_drain},8" ) # 0: auto ranging # 11 - 1nA Limited (matches EasyExpert)
        # Sweep setup
        #self.b1500.write( f"MM 2,{smu_ch},{smu_ch_drain}" ) # Staircase sweep measurement on SMU1
        #orig which works pretty well 
        #self.b1500.write( f"MM 2,{smu_ch}" ) # Staircase sweep measurement on SMU1
        #self.b1500.write( f"MM 2,{smu_ch_drain}" ) # Staircase sweep measurement on SMU1
        #modifided to hopefully caputre gate and drain current 
        self.b1500.write( f"MM 2, {smu_ch_drain}, {smu_ch}" ) # Staircase sweep measurement on SMU1
        ###CM Originally compliance measurement
        #self.b1500.write( f"CMM {smu_ch},0" ) # 0: compliance side measurement, 1: current measurement
        ###CM changed to current measurement
        self.b1500.write( f"CMM {smu_ch},1" ) # 0: compliance side measurement, 1: current measurement
        self.b1500.write( f"RI {smu_ch},11" ) # 0: auto ranging # 11 - 1nA Limited (matches EasyExpert)
        #self.b1500.write( f"WT 0,0,0" ) # hold, delay, s_delay to 0
        #QnM codeline
        self.b1500.write( f"WT 0,100e-6,100e-6" ) # hold, delay, s_delay to 0
        #self.b1500.write( f"WT 0,0,0" ) # hold, delay, s_delay to 0
        
        self.b1500.write( f"WM 1,1" ) # A,B - A =1 keep going if we hit compliance, A=2 abort if we hit compliance, B=1 = return to START val after meas, B=2 =stay at STOP val after meas
        
        # WV Command
        # WV chnum,mode,range,start,stop,step[,Icomp[,Pcomp]]
        # mode: 1 - Linear,  2 - Log, 3: Linear bidirectional, 4: Log bidirectional
        self.b1500.write( f"WV {smu_ch},{mode},0,{vstart},{vstop},{nsteps},{icomp:.2E}")
        self.b1500.write( "TSR" ) # Reset timestamp for all channels
        
        self.b1500.write( "XE" ) # Execute measurement
        
        op_done = self.b1500.query( "*OPC?" ) # should block until operation completes, I think
        #print( f"OP_DONE: {op_done.strip()}" )
        
        
        # Reset Measurement SMU
        if disconnect_after:
            self.b1500.write( f"CL {smu_ch}" ) # Disconnect sweep SMU
            self.b1500.write( f"CL {smu_ch_drain}" ) # Disconnect drain SMU
        # Read data
        data = self.b1500.read()
        
        #process data
        drain_times , drain_currents, gate_times, gate_currents, gate_voltages = self.process_data_str_IDnVGnIG(data)
        
        plot_handles = ()
        if plot_data:
            fig, (ax1,ax2) = plt.subplots(nrows=1,ncols=2)
            ax1.plot( gate_voltages , drain_currents , linestyle="-" , color="b", markersize=2 )
            ax1.set_yscale('log')
            ax1.set_xlabel( 'Gate Voltage (V)' )
            ax1.set_ylabel( 'Drain Current (A)' )
            
            ax2.plot(gate_voltages, gate_currents, linestyle="-" , color="r", markersize=2 ) 
            ax2.set_yscale('log')
            ax2.set_xlabel( 'Gate Voltage (V)' )
            ax2.set_ylabel( 'Gate Current (A)' )
            
# =============================================================================
#             resistance = voltage / current
#             ax[1].plot( voltage , resistance  , linestyle="-" , color="r", markersize=2 )
#             ax[1].set_xlabel( 'Voltage (V)' )
#             ax[1].set_ylabel( 'Resistance ($\Omega$)' )
# =============================================================================
            
            fig.tight_layout()
            
            plt.show(block=False)
        
        return drain_times , drain_currents, gate_times, gate_currents, gate_voltages