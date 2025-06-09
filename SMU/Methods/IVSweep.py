import matplotlib.pyplot as plt

def IVSweep(self, 
    b1500=None, 
    param_name=None,
    smu_nums = None,
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
    t_period = None,
    **overrides
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
    # Collect defaults into a dict
    final_params = {
    "smu_nums": smu_nums,
    "vstart": vstart,
    "vstop": vstop,
    "icomp": icomp,
    "nsteps": nsteps,
    "connect_first": connect_first,
    "disconnect_after": disconnect_after,
    "plot_data": plot_data,
    "PULSED_SWEEP": PULSED_SWEEP,
    "mode": mode,
    "t_pulse": t_pulse,
    "t_period": t_period
    }
    
    # Load from parameters if specified
    if b1500 and param_name:
        param_block = dict(b1500.parameters.get(param_name, {}))
        param_block.update(overrides)
        for key, value in param_block.items():
            setattr(b1500, f"{key}_{param_name}", value)
        final_params.update(param_block)

    if not b1500 or not param_name:
        final_params.update(overrides)
    
    smu_nums = final_params["smu_nums"]
    vstart = final_params["vstart"]
    vstop = final_params["vstop"]
    icomp = final_params["icomp"]
    nsteps = final_params["nsteps"]
    connect_first = final_params["connect_first"]
    disconnect_after = final_params["disconnect_after"]
    plot_data = final_params["plot_data"]
    PULSED_SWEEP = final_params["PULSED_SWEEP"]
    mode = final_params["mode"]
    t_pulse = final_params["t_pulse"]
    t_period = final_params["t_period"]
    
    
    
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
        print(f"compliance current is: {icomp}")
        results = self.smu_meas_sweep(b1500 = b1500, smu_nums = smu_nums , vstart=vstart , vstop=vstop , nsteps=nsteps , mode=mode, icomp=icomp, num_averaging_samples=1 , connect_first=True, disconnect_after=True , plot_data=True)
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

