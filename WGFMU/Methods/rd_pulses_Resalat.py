import time
def rd_pulses_Resalat(self, b1500, alternate_waveform = None, num_reads=1, offset_times = False, v_rd = None):
    # clear existing pattern data
    self.wg.WGFMU_clear()
    
    if v_rd is not None:
        # print("Overriding Read Value")
        # Create waveform on WGFMU
        self.create_waveform(b1500, alternate_waveform = alternate_waveform, OverrideValue = [("Read", v_rd)])
        
        # Run pattern
        t_run = time.perf_counter()
        self.wgfmu_run([b1500.test_info.ch_vdd , b1500.test_info.ch_vss ], open_first=True, close_after=True)
        
        # Read out data
        times1, vals1 = self.read_results( b1500.test_info.ch_vdd )
        
        # Close down WGFMU Session
        times = times1
        currents = vals1
        conductances = currents / (.1) #CHANGE THIS WE NEED TO MAKE THE READ VOLTAGE INPUT HERE ITS HARD CODED FOR NOW
        
        if offset_times:
            times += t_run
        
        return ( times , currents , conductances , t_run)
    
    