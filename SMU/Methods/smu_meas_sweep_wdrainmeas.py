def smu_meas_sweep_wdrainmeas(self, smu_num, smudchan, smudrain_bias, vstart=0.0, vstop=0.10, 
                               nsteps=51, mode=1, icomp=100e-3, num_averaging_samples=1, 
                               connect_first=True, disconnect_after=True, vmax_override=False, plot_data=False):
    """
    Performs a voltage sweep while measuring both gate and drain currents.

    Parameters:
    - smu_num (int): SMU channel number for Gate
    - smudchan (int): SMU channel number for Drain
    - smudrain_bias (float): Drain voltage bias
    - vstart, vstop (float): Sweep voltage range
    - nsteps (int): Number of steps in the sweep
    - mode (int): Sweep mode (1 = Linear, 2 = Log, etc.)
    - icomp (float): Compliance current limit (default: 100mA)
    - num_averaging_samples (int): Number of averaging samples
    - connect_first (bool): Connect SMUs before measurement
    - disconnect_after (bool): Disconnect SMUs after measurement
    - vmax_override (bool): Allow voltage above 7V if True
    - plot_data (bool): Plot results if True

    Returns:
    - drain_times, drain_currents, gate_times, gate_currents, gate_voltages
    """
    VMAX = 7
    if ((abs(vstart) > VMAX) or (abs(vstop) > VMAX)) and not vmax_override:
        raise ValueError("Voltage exceeds 7V! Set vmax_override=True to proceed.")

    smu_ch = self.smus[smu_num - 1]
    smu_ch_drain = self.smus[smudchan - 1]

    # Configure measurement settings
    self.b1500.write("FMT 1,1")
    self.b1500.write("TSC 1")
    self.b1500.write("FL 1")
    self.b1500.write(f"AV {num_averaging_samples},0")
    self.b1500.write(f"AAD {smu_ch},1")
    self.b1500.write(f"AAD {smu_ch_drain},1")

    # Connect SMUs
    if connect_first:
        self.b1500.write(f"CN {smu_ch_drain}")
        self.b1500.write(f"DV {smu_ch_drain},0,{smudrain_bias}")
        self.b1500.write(f"CN {smu_ch}")
        self.b1500.write(f"DV {smu_ch},0,{vstart}")

    # Configure drain measurement
    self.b1500.write(f"CMM {smu_ch_drain},1")
    self.b1500.write(f"RI {smu_ch_drain},8")

    # Configure sweep mode
    self.b1500.write(f"MM 2,{smu_ch_drain},{smu_ch}")
    self.b1500.write(f"CMM {smu_ch},1")
    self.b1500.write(f"RI {smu_ch},11")
    self.b1500.write("WT 0,100e-6,100e-6")
    self.b1500.write("WM 1,1")

    # Set up voltage sweep
    self.b1500.write(f"WV {smu_ch},{mode},0,{vstart},{vstop},{nsteps},{icomp:.2E}")
    self.b1500.write("TSR")

    # Execute measurement
    self.b1500.write("XE")
    self.b1500.query("*OPC?")

    # Disconnect SMUs if required
    if disconnect_after:
        self.b1500.write(f"CL {smu_ch}")
        self.b1500.write(f"CL {smu_ch_drain}")

    # Read and process data
    data = self.b1500.read()
    drain_times, drain_currents, gate_times, gate_currents, gate_voltages = self.process_data_str_IDnVGnIG(data)

    # Optional plotting
    if plot_data:
        fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2)
        ax1.plot(gate_voltages, drain_currents, linestyle="-", color="b")
        ax1.set_yscale("log")
        ax1.set_xlabel("Gate Voltage (V)")
        ax1.set_ylabel("Drain Current (A)")

        ax2.plot(gate_voltages, gate_currents, linestyle="-", color="r")
        ax2.set_yscale("log")
        ax2.set_xlabel("Gate Voltage (V)")
        ax2.set_ylabel("Gate Current (A)")

        fig.tight_layout()
        plt.show()

    return drain_times, drain_currents, gate_times, gate_currents, gate_voltages
