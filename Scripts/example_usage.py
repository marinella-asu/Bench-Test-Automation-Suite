from B1500.B1500Unified import B1500
import numpy as np
import matplotlib.pyplot as plt


# Define experiment parameters
parameters = {
    "Name": "Evan",
    "Test Number": "1",
    "Die Number": 1,
    "Device Number": 67,
    "Interval": 10e-3,
    "data_points": 300,
    "v_rd": 1,
    "Waveform Format": "Reram",  # Loads "Reram.txt"
    "Waveform": "Evan_Reram_4",
    "Waveform Editor": "ask",   
    "VDD WGFMU": 1,
    "VSS WGFMU": 2

}

v_rd = 1  # Default for NSTEPS: Set an NSTEPS parameter if you want this to be different
data_points = 300
interval = 1.5e-3

    

# Initialize Unified B1500 (includes parameter validation)
b1500 = B1500(unit_label = 'A', parameters=parameters)

#Gate is SMU2
#Drain is SMU4

smu_numD = 4
smu_numG = 1
smu_numS = 3
smu_numB = 2

results_read = b1500.smu.smu_meas_sample_multi_term_int(smu_numD = smu_numD, 
                                    smu_numG = smu_numG, 
                                    smu_numS = smu_numS, 
                                    smu_numB = smu_numB, 
                                    vmeasD=0,
                                    vmeasG=b1500.v_rd,
                                    vmeasS=0, 
                                    vmeasB=0,
                                    icompDSB=1e-6, 
                                    icompG=1e-6,  
                                    interval=b1500.Interval,
                                    pre_bias_time=0, 
                                    number=b1500.data_points, 
                                    disconnect_after=False, 
                                    plot_results=False,
                                    int_num = 50)

print(results_read) #I wanna see what format the data is in
data = b1500.data_clean(b1500, results_read, parameters)
time_drain = data.get("SMU4_Time", None)
current_drain = data.get("SMU4_Current", None)
time_gate = data.get("SMU1_Time", None)
current_gate = data.get("SMU1_Current", None)

current_drain = current_drain

fig, axs = plt.subplots(2, 1, figsize=(8, 6))  # Increase figure size

# First plot: Gate Current vs. Time
axs[0].plot(time_gate, current_gate, marker="o", linestyle="-", label="Gate Current")
axs[0].set_xlabel("Time (s)", fontsize=10)
axs[0].set_ylabel("Current (A)", fontsize=10)
axs[0].legend(fontsize=9, loc="upper right")
axs[0].grid(True, linestyle="--", linewidth=0.5, alpha=0.7)

# Rotate the x-axis labels to avoid overlap
axs[0].tick_params(axis='x', rotation=45)  # Rotate x-axis labels

# Second plot: Drain Current vs. Time
axs[1].plot(time_drain, current_drain, marker="o", linestyle="-", label="Drain Current", color="red")
axs[1].set_xlabel("Time (s)", fontsize=10)
axs[1].set_ylabel("Current (A)", fontsize=10)
axs[1].legend(fontsize=9, loc="upper right")
axs[1].grid(True, linestyle="--", linewidth=0.5, alpha=0.7)

# Rotate the x-axis labels to avoid overlap
axs[1].tick_params(axis='x', rotation=45)  # Rotate x-axis labels

# Automatically adjust layout to make room for the rotated labels
plt.tight_layout()

# Show the plot
plt.show()
