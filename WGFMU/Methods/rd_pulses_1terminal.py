import time
def rd_pulses_1terminal(self, b1500, ch_vdd, ch_vss,
                num_reads=1, t_start=1e-6, t_settle=3e-6, t_read=10e-3,
                rd_period=100e-3, meas_pts=1, meas_interval=-1, meas_averaging=-1,
                t_rise=100e-9, v_rd=.1,  v_off=0.0,
                range_rd=None,
                offset_times=False, wgfmu_open_first=True, wgfmu_close_after=True, alternate_waveform = None):
    # clear existing pattern data
    self.wg.WGFMU_clear()
    
    # Create waveform on WGFMU
    self.create_waveform(b1500, alternate_waveform = alternate_waveform, OverrideValue = ["Read", v_rd], num_copies = num_reads, meas_pts1=meas_pts, meas_interval1=meas_interval)
        
    
    # Run pattern
    t_run = time.perf_counter()
    self.wgfmu_run( [ch_vdd,ch_vss], open_first=wgfmu_open_first, close_after=wgfmu_close_after )
    
    # Read out data
    times1, vals1 = self.read_results( ch_vdd )
    
    # Close down WGFMU Session
    times = times1
    currents = vals1
    conductances = currents / (v_rd)
    
    # print(times)
    # print(currents)
    # print(conductances)
        
    if offset_times:
        times += t_run
    
    return ( times , currents , conductances)