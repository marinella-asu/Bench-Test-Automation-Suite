import time
def rd_pulses_Resalat(self, b1500, alternate_waveform = None, num_reads=1, offset_times = False):
    # clear existing pattern data
    self.wg.WGFMU_clear()
    
    # Create waveform on WGFMU
    self.create_waveform(b1500.test_info, alternate_waveform = alternate_waveform)
    
    # Run pattern
    t_run = time.perf_counter()
    self.wgfmu_run([b1500.test_info.ch_vdd , b1500.test_info.ch_vss ])
    
    # Read out data
    times1, vals1 = self.read_results( b1500.test_info.ch_vdd )
    times2, vals2 = self.read_results( b1500.test_info.ch_vss )
    
    # Close down WGFMU Session
    times = times1
    currents = vals1
    conductances = currents / (b1500.test_info.VDD_rd)
    
    if offset_times:
        times += t_run
    
    return ( times , currents , conductances , t_run)