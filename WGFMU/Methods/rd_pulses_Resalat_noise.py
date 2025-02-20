import time

def rd_pulses_Resalat_noise(self, TestInfo, alternate_waveform=None, num_reads=1, offset_times=False):
    """
    Runs a read pulse measurement for noise characterization using WGFMU.

    Parameters:
    - self: Class instance containing WGFMU control functions.
    - TestInfo: Object containing test parameters.
    - alternate_waveform: Optional alternative waveform to apply.
    - num_reads: Number of read pulses.
    - offset_times: Boolean flag to offset times by execution time.

    Returns:
    - times (numpy array): Time data.
    - currents (numpy array): Current data.
    - conductances (numpy array): Conductance values.
    - t_run (float): Execution timestamp.
    """

    # Clear existing pattern data
    self.wg.WGFMU_clear()
    
    # Create waveform on WGFMU
    self.create_waveform(TestInfo, alternate_waveform=alternate_waveform)

    # Run measurement pattern
    t_run = time.perf_counter()
    self.wgfmu_run([TestInfo.ch_vdd, TestInfo.ch_vss])

    # Read out data
    times1, vals1 = self.read_results(TestInfo.ch_vdd)
    times2, vals2 = self.read_results(TestInfo.ch_vss)

    # Process results
    times = times1
    currents = vals1
    conductances = currents / (TestInfo.VDD_rd)

    if offset_times:
        times += t_run

    return times, currents, conductances, t_run
