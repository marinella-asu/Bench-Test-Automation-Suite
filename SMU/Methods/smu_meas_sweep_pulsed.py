import matplotlib.pyplot as plt
import numpy as np
def smu_meas_sweep_pulsed(self, smu_nums, vstart=0.0, vstop=0.10, t_pulse=500e-6, t_period=1e-3, 
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


    # Resolve SMU channels from numbers
    smu_channels = [self.smus[num - 1] for num in smu_nums]  # Convert SMU numbers to channels
    smu_channels_str = ", ".join(map(str, smu_channels))

    # Measurement settings
    self.b1500.write("FMT 1,1")
    self.b1500.write("TSC 1")
    self.b1500.write("FL 1")
    self.b1500.write(f"AV {num_averaging_samples},0")
    for smu_ch in smu_channels:
        self.b1500.write(f"AAD {smu_ch},2")  # High-speed ADC for pulsed measurement
    self.b1500.write(f"AIT 2,3,{t_pulse/2}")  # Set measurement time to half of pulse width
    self.b1500.write(f"PT 0,{t_pulse},{t_period}")  # Set pulse parameters

    # Connect SMU
    if connect_first:
        self.b1500.write(f"CN {smu_channels_str}")
        self.b1500.write(f"DV {smu_ch},0,{vstart}")

    # Configure pulsed sweep
    for smu_ch in smu_channels:
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
        for smu_ch in smu_channels:
            self.b1500.write(f"CL {smu_ch}")

    # Read and process data
    data = self.data_clean(self.b1500.read())  # Returns a DataFrame

    # Extract dynamic columns for each SMU
    extracted_data = []
    for smu_num in smu_nums:
        time_col = f"SMU{smu_num}_Time (s)"
        voltage_col = f"SMU{smu_num}_Voltage (V)"
        current_col = f"SMU{smu_num}_Current (A)"

        try:
            time_values = data[time_col].to_numpy(dtype=np.float64)
            voltage_values = data[voltage_col].to_numpy(dtype=np.float64)
            current_values = data[current_col].to_numpy(dtype=np.float64)

        except KeyError as e:
            missing_col = str(e).strip("'")
            print(f"❌ Missing expected column in processed data: {missing_col}\n Returning data array")
            return data  # Return full dataset if missing columns

        # If plot_data is enabled, generate an I-V plot
        if plot_data:
            plt.figure(figsize=(6, 4))  # Keep it compact
            plt.plot(voltage_values, current_values, marker="o", linestyle="-", label=f"SMU {smu_num}")
            
            # Minimal axis labels
            plt.xlabel("Voltage (V)", fontsize=10)
            plt.ylabel("Current (A)", fontsize=10)
            plt.xticks(fontsize=8)
            plt.yticks(fontsize=8)
            
            # Sparse labeling
            plt.tick_params(axis="both", which="both", direction="in", length=3)
            
            plt.legend(fontsize=9, loc="upper left")
            plt.grid(True, linestyle="--", linewidth=0.5, alpha=0.7)
            plt.show()

    # If only one SMU, return time, voltage, and current separately
    if len(smu_nums) == 1:
        return time_values, voltage_values, current_values # Unpack tuple for single SMU

    # If multiple SMUs, return structured NumPy array
    structured_data = np.column_stack([np.hstack(data) for data in extracted_data])
    print(f"📦 Returning structured NumPy array with shape {structured_data.shape}")
    return structured_data