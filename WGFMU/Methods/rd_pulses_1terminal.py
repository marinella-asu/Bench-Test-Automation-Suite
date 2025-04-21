import time
def rd_pulses_1terminal(self, b1500, alternate_waveform = None, num_reads=1, offset_times = False):
    # --- WGFMU / Measurement Timing & Channel Configuration ---------------------
    num_reads = 1       # Reads per verification loop; override with Num_Reads
    if hasattr(b1500.test_info, "Num_Reads"):
        num_reads = b1500.test_info.Num_Reads

    t_start = 598.9e-6  # Start‑delay before first pulse; override with T_Start
    if hasattr(b1500.test_info, "T_Start"):
        t_start = b1500.test_info.T_Start

    t_settle = 1e-6     # Settling time after programming; override with T_Settle
    if hasattr(b1500.test_info, "T_Settle"):
        t_settle = b1500.test_info.T_Settle

    t_read = 100e-6     # Duration of each read window; override with T_Read
    if hasattr(b1500.test_info, "T_Read"):
        t_read = b1500.test_info.T_Read

    rd_period = 1e-3    # Period between reads; override with Rd_Period
    if hasattr(b1500.test_info, "Rd_Period"):
        rd_period = b1500.test_info.Rd_Period

    meas_pts = 1        # Averaging count (WGFMU measure points); override with Meas_Pts
    if hasattr(b1500.test_info, "Meas_Pts"):
        meas_pts = b1500.test_info.Meas_Pts

    meas_interval = -1  # Interval between measure points; override with Meas_Interval
    if hasattr(b1500.test_info, "Meas_Interval"):
        meas_interval = b1500.test_info.Meas_Interval

    meas_averaging = -1 # Averaging time; override with Meas_Averaging
    if hasattr(b1500.test_info, "Meas_Averaging"):
        meas_averaging = b1500.test_info.Meas_Averaging

    t_rise = 100e-9     # Pulse rise‑time; override with T_Rise
    if hasattr(b1500.test_info, "T_Rise"):
        t_rise = b1500.test_info.T_Rise

    v_rd = 0.1          # Read voltage; override with V_Read
    if hasattr(b1500.test_info, "V_Read"):
        v_rd = b1500.test_info.V_Read

    v_off = 0.0         # Post‑pulse offset voltage; override with V_Offset
    if hasattr(b1500.test_info, "V_Offset"):
        v_off = b1500.test_info.V_Offset

    range_rd = wgc.WGFMU_MEASURE_CURRENT_RANGE_100UA  # WGFMU read‑current range; override with Range_Read
    if hasattr(b1500.test_info, "Range_Read"):
        range_rd = b1500.test_info.Range_Read

    offset_times = False        # Whether to offset all times to zero; override with Offset_Times
    if hasattr(b1500.test_info, "Offset_Times"):
        offset_times = bool(b1500.test_info.Offset_Times)

    wgfmu_open_first = True     # Open WGFMU at sequence start; override with WG_Open_First
    if hasattr(b1500.test_info, "WG_Open_First"):
        wgfmu_open_first = bool(b1500.test_info.WG_Open_First)

    wgfmu_close_after = True    # Close WGFMU at sequence end; override with WG_Close_After
    if hasattr(b1500.test_info, "WG_Close_After"):
        wgfmu_close_after = bool(b1500.test_info.WG_Close_After)

    VREF = 0            # External reference voltage (if used); override with VREF
    if hasattr(b1500.test_info, "VREF"):
        VREF = b1500.test_info.VREF

    
    # clear existing pattern data
    self.wg.WGFMU_clear()
    
    # Create waveform on WGFMU
    self.create_waveform(b1500.test_info, alternate_waveform = alternate_waveform)
        
    
    # Run pattern
    t_run = time.perf_counter()
    self.wgfmu_run( [ch_vdd,ch_vss], open_first=wgfmu_open_first, close_after=wgfmu_close_after )
    
    # Read out data
    times1, vals1 = self.read_results( ch_vdd )
    
    # Close down WGFMU Session
    times = times1
    currents = vals1
    conductances = currents / (v_rd-VREF)
    
    if offset_times:
        times += t_run
    
    return ( times , currents , conductances)