import time
def rd_pulses_Resalat(self, TestInfo, alternate_waveform = None, num_reads=1, offset_times = False):
    # clear existing pattern data
    self.wg.WGFMU_clear()
    
    # Create waveform on WGFMU
    self.create_waveform(TestInfo, alternate_waveform = alternate_waveform)
    
    # Run pattern
    t_run = time.perf_counter()
    self.wgfmu_run([TestInfo.ch_vdd , TestInfo.ch_vss ])
    
    # Read out data
    times1, vals1 = self.read_results( TestInfo.ch_vdd )
    times2, vals2 = self.read_results( TestInfo.ch_vss )
    
    # Close down WGFMU Session
    times = times1
    currents = vals1
    conductances = currents / (TestInfo.VDD_rd)
    
    if offset_times:
        times += t_run
    
    return ( times , currents , conductances , t_run)