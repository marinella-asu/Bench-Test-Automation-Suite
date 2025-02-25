import matplotlib.pyplot as plt

def IVSweep(
    self,
    smu_nums,
    vstart=0,
    vstop=0.1,
    icomp=100e-3,
    nsteps=101,
    connect_first=True,
    disconnect_after=True,
    plot_data = False,
    PULSED_SWEEP = False,
    mode = 3,
    t_pulse = None,
    t_period = None
):
    """
    Performs an IV sweep on a specified SMU channel with visualization and result printing.

    Parameters:
        smu_num (int): The SMU channel number.
        vstart (float): Start voltage for the sweep.
        vstop (float): Stop voltage for the sweep.
        icomp (float): Compliance current.
        nsteps (int): Number of steps in the sweep.
        connect_first (bool): Whether to connect the SMU before measurement.
        disconnect_after (bool): Whether to disconnect the SMU after measurement.
        plot_data (bool): Plot results if True

    Returns:
        dict: A dictionary containing 'voltages', 'currents', and 'timestamps'.
    """
    
    self.connect_smu_list([1])
    self.bias_smu(1, 0, 100e-3 )
    self.connect_smu_list([2])
    self.bias_smu(2, 0, 100e-3 )
    self.connect_smu_list([3])
    self.bias_smu(3, 0, 100e-3)
    self.connect_smu_list([4])
    self.bias_smu(4, 0, 100e-3 )
    
    # Perform the IV sweep using the core SMU functionality
    print(f"Starting IV Sweep on SMU {smu_nums}...")
    if not PULSED_SWEEP:
        results = self.smu_meas_sweep( smu_nums , vstart=vstart , vstop=vstop , nsteps=nsteps , mode=mode, icomp=icomp, num_averaging_samples=1 , connect_first=True, disconnect_after=True , plot_data=True)
    else:
        results = self.smu_meas_sweep_pulsed(
                                smu_nums,
                                vstart=vstart, 
                                vstop=vstop, 
                                t_pulse=t_pulse,
                                t_period=t_period,
                                nsteps=nsteps, 
                                mode=mode,
                                icomp=icomp,
                                num_averaging_samples=1,
                                connect_first=True,
                                disconnect_after=True ,
                                plot_data=True,
                                )
    print("Finished, Now returning results")
    # Return the results as a dictionary
    return results

