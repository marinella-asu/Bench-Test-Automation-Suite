import matplotlib.pyplot as plt

def IVSweep(
    self,
    smu_num,
    vstart=0,
    vstop=0.1,
    icomp=100e-3,
    nsteps=101,
    plot_data=True,
    connect_first=True,
    disconnect_after=True,
):
    """
    Performs an IV sweep on a specified SMU channel with visualization and result printing.

    Parameters:
        smu_num (int): The SMU channel number.
        vstart (float): Start voltage for the sweep.
        vstop (float): Stop voltage for the sweep.
        icomp (float): Compliance current.
        nsteps (int): Number of steps in the sweep.
        plot_data (bool): Whether to plot the results.
        connect_first (bool): Whether to connect the SMU before measurement.
        disconnect_after (bool): Whether to disconnect the SMU after measurement.

    Returns:
        dict: A dictionary containing 'voltages', 'currents', and 'timestamps'.
    """
    # Perform the IV sweep using the core SMU functionality
    print(f"Starting IV Sweep on SMU {smu_num}...")
    results = self.smu_meas_sweep(
        smu_num,
        vstart=vstart,
        vstop=vstop,
        nsteps=nsteps,
        mode=1,
        icomp=icomp,
        num_averaging_samples=1,
        connect_first=connect_first,
        disconnect_after=disconnect_after,
        plot_data=False,  # Disable plotting in the core function
    )

    # Extract voltages, currents, and timestamps
    voltages = results["voltages"]
    currents = results["currents"]
    timestamps = results["timestamps"]

    # Print results
    print(f"IV Sweep Completed on SMU {smu_num}.")
    print(f"Start Voltage: {vstart} V, Stop Voltage: {vstop} V")
    print(f"Compliance Current: {icomp} A")
    print(f"Number of Steps: {nsteps}")
    print("Results:")
    for i, (v, i_current, t) in enumerate(zip(voltages, currents, timestamps)):
        print(f"Step {i+1}: Voltage={v:.3f} V, Current={i_current:.3e} A, Time={t:.3f} s")

    # Plot results if requested
    if plot_data:
        plt.figure(figsize=(8, 6))
        plt.plot(voltages, currents, marker="o", linestyle="-", color="b")
        plt.title(f"IV Sweep Results for SMU {smu_num}")
        plt.xlabel("Voltage (V)")
        plt.ylabel("Current (A)")
        plt.grid(True)
        plt.show()

    # Return the results as a dictionary
    return results

