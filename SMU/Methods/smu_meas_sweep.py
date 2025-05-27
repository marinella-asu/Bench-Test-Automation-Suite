import numpy as np
import matplotlib.pyplot as plt

def smu_meas_sweep(self, b1500 = None, smu_nums = None, vstart=0.0, vstop=0.10, nsteps=51, mode=1, icomp=100e-3, 
                    num_averaging_samples=1, connect_first=True, disconnect_after=True, 
                    vmax_override=False, plot_data = False):
    """
    Performs a staircase voltage sweep measurement on multiple SMUs.

    Parameters:
    - smu_nums (list): List of SMU channel numbers (e.g., [1, 2, 3])
    - vstart (float): Start voltage
    - vstop (float): Stop voltage
    - nsteps (int): Number of steps in the sweep
    - mode (int): Sweep mode (1 = Linear, 2 = Log, 3 = Linear Bi-dir, 4 = Log Bi-dir)
    - icomp (float): Compliance current limit (default: 100mA)
    - num_averaging_samples (int): Number of averaging samples
    - connect_first (bool): Connect SMU before measurement (default: True)
    - disconnect_after (bool): Disconnect SMU after measurement (default: True)
    - vmax_override (bool): Allow voltage above 7V if True

    Returns:
    - NumPy array containing structured measurement data if multiple SMUs
    - (times, voltage, current) if a single SMU
    """

    VMAX = 7  # Maximum safe voltage limit
    if ((abs(vstart) > VMAX) or (abs(vstop) > VMAX)) and not vmax_override:
        raise ValueError("Voltage exceeds 7V! Set vmax_override=True to proceed.")
        
    if isinstance(smu_nums, int):
        smu_nums = [smu_nums]
    # Resolve SMU channels from numbers
    smu_channels = [self.smus[num - 1] for num in smu_nums]  # Convert SMU numbers to channels
    smu_channels_str = ", ".join(map(str, smu_channels))

    # Configure measurement settings
    self.b1500.write("FMT 1,1")
    self.b1500.write("TSC 1")  # Enable timestamp output
    self.b1500.write("FL 1")  # Disable SMU filter
    self.b1500.write(f"AV {num_averaging_samples},0")  # Set averaging samples

    # Enable HR ADC for each SMU
    for smu_ch in smu_channels:
        self.b1500.write(f"AAD {smu_ch},1")  

    # Connect SMUs and set initial voltage
    if connect_first:
        for smu_ch in smu_channels:
            self.b1500.write(f"CN {smu_ch}")
            self.b1500.write(f"DV {smu_ch},0,{vstart}")

    # Configure sweep mode for multiple SMUs
    self.b1500.write(f"MM 2, {smu_channels_str}")  # Multi-SMU measurement
    for smu_ch in smu_channels:
        self.b1500.write(f"CMM {smu_ch},0")  # Compliance-side measurement
        self.b1500.write(f"RI {smu_ch},0")  # Auto-ranging
    self.b1500.write("WT 0,0,0")  # Zero hold, delay, and step delay

    # Set up voltage sweep
    for smu_ch in smu_channels:
        self.b1500.write(f"WV {smu_ch},{mode},0,{vstart},{vstop},{nsteps},{icomp:.2E}")
    self.b1500.write("TSR")  # Reset timestamp

    # Execute measurement
    self.b1500.write("XE")
    self.b1500.query("*OPC?")  # Block until operation completes

    # Disconnect SMUs if required
    if disconnect_after:
        for smu_ch in smu_channels:
            self.b1500.write(f"CL {smu_ch}")

    # Read and process data
    data = b1500.data_clean(b1500, self.b1500.read(), b1500.test_info.parameters, NoSave = True)  # Returns a DataFrame

    # Extract dynamic columns for each SMU
    extracted_data = []
    for smu_num in smu_nums:
        time_col = f"SMU{smu_num}_Time"
        voltage_col = f"SMU{smu_num}_Voltage"
        current_col = f"SMU{smu_num}_Current"

        try:
            time_values = data[time_col].astype(float)
            voltage_values = data[voltage_col].astype(float)
            current_values = data[current_col].astype(float)

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
    return time_values, voltage_values, current_values
