def smu_meas_sweep_pulsed(self, smu_num, vstart=0.0, vstop=0.10, t_pulse=500e-6, t_period=1e-3, 
                           nsteps=51, mode=1, icomp=100e-3, num_averaging_samples=1, 
                           connect_first=True, disconnect_after=True, vmax_override=False, plot_data=False):
    """
    Performs a pulsed voltage sweep measurement on an SMU.

    Parameters:
    - smu_num (int): SMU channel number
    - vstart (float): Start voltage
    - vstop (float): Stop voltage
    - t_pulse (float): Pulse width (0.5ms to 2ms)
    - t_period (float): Pulse period (5ms to 5000ms)
    - nsteps (int): Number of steps in the sweep
    - mode (int): Sweep mode (1 = Linear, 2 = Log, etc.)
    - icomp (float): Compliance current limit (default: 100mA)
    - num_averaging_samples (int): Number of averaging samples
    - connect_first (bool): Connect SMU before measurement
    - disconnect_after (bool): Disconnect SMU after measurement
    - vmax_override (bool): Allow voltage above 7V if True
    - plot_data (bool): Plot results if True

    Returns:
    - times, voltage, current (numpy arrays)
    """
    assert 500e-6 <= t_pulse <= 2e-3, "Pulse width must be 0.5ms to 2ms!"
    assert 5e-3 <= t_period <= 5000e-3, "Pulse period must be 5ms to 5000ms!"

    smu_ch = self.smus[smu_num - 1]

    # Measurement settings
    self.b1500.write("FMT 1,1")
    self.b1500.write("TSC 1")
    self.b1500.write("FL 1")
    self.b1500.write(f"AV {num_averaging_samples},0")
    self.b1500.write(f"AAD {smu_ch},2")  # High-speed ADC for pulsed measurement
    self.b1500.write(f"AIT 2,3,{t_pulse/2}")  # Set measurement time to half of pulse width
    self.b1500.write(f"PT 0,{t_pulse},{t_period}")  # Set pulse parameters

    # Connect SMU
    if connect_first:
        self.b1500.write(f"CN {smu_ch}")
        self.b1500.write(f"DV {smu_ch},0,{vstart}")

    # Configure pulsed sweep
    self.b1500.write(f"MM 4,{smu_ch}")
    self.b1500.write(f"CMM {smu_ch},0")
    self.b1500.write(f"RI {smu_ch},11")
    self.b1500.write("WT 0,0,0")
    self.b1500.write(f"PWV {smu_ch},{mode},0,0,{vstart},{vstop},{nsteps},{icomp:.3E}")
    self.b1500.write("TSR")

    # Execute measurement
    self.b1500.write("XE")
    self.b1500.query("*OPC?")

    # Disconnect SMU if required
    if disconnect_after:
        self.b1500.write(f"CL {smu_ch}")

    # Read and process data
    data = self.b1500.read()
    times, voltage, current = self.process_data_str_tiv(data)

    # Optional plotting
    if plot_data:
        fig, ax = plt.subplots(nrows=1, ncols=2)
        ax[0].plot(voltage, current, linestyle="-", color="b")
        ax[0].set_xlabel("Voltage (V)")
        ax[0].set_ylabel("Current (A)")

        ax[1].plot(voltage, voltage / current, linestyle="-", color="r")
        ax[1].set_xlabel("Voltage (V)")
        ax[1].set_ylabel("Resistance (Ω)")

        fig.tight_layout()
        plt.show()

    return times, voltage, current
