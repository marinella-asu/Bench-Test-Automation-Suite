from B1500.B1500Unified import B1500
import numpy as np
import matplotlib.pyplot as plt


# Define experiment parameters
parameters = {
    "Name": "Evan",
    "Test Number": "ask",
    "Die Number": 1,
    "Device Number": 67,
    "Waveform Format": "Reram",  # Loads "Reram.txt"
    "Waveform": "Evan_Reram_4",
    # "Waveform Editor": "ask",   
    "VDD WGFMU": 1,
    "VSS WGFMU": 2,
    "Interval": 1.5e-3,
    "data points": 300,
    "v rd": 1
}


# Initialize Unified B1500 (includes parameter validation)
b1500 = B1500(unit_label = 'A', parameters=parameters)

#Gate is SMU2
#Drain is SMU4

smu_numD = 1
smu_numG = 4 
smu_numS = 3
smu_numB = 2

results_read = b1500.smu.smu_meas_sample_multi_term_int(smu_numD = smu_numD, 
                                    smu_numG = smu_numG, 
                                    smu_numS = smu_numS, 
                                    smu_numB = smu_numB, 
                                    vmeasD=0,
                                    vmeasG=b1500.test_info.v_rd,
                                    vmeasS=0, 
                                    vmeasB=0,
                                    icompDSB=1e-6, 
                                    icompG=1e-6,  
                                    interval=b1500.test_info.Interval,
                                    pre_bias_time=0, 
                                    number=b1500.test_info.data_points, 
                                    disconnect_after=False, 
                                    plot_results=False,
                                    number = 50)

print(results_read) #I wanna see what format the data is in
data = b1500.data_clean(b1500, results_read, parameters)
time_gate = data.get("SMU4_Time", None)
current_gate = data.get("SMU4_Current", None)
time_drain = data.get("SMU1_Time", None)
current_drain = data.get("SMU1_Current", None)

# Create a figure with two subplots
fig, axs = plt.subplots(2, 1, figsize=(6, 6), sharex=True)

# First plot: Gate Current vs. Time
axs[0].plot(time_gate, current_gate, marker="o", linestyle="-", label="Gate Current")
axs[1].set_xlabel("Time (s)", fontsize=10)
axs[0].set_ylabel("Current (A)", fontsize=10)
axs[0].legend(fontsize=9, loc="upper right")
axs[0].grid(True, linestyle="--", linewidth=0.5, alpha=0.7)

# Second plot: Drain Current vs. Time
axs[1].plot(time_drain, current_drain, marker="o", linestyle="-", label="Drain Current", color="red")
axs[1].set_xlabel("Time (s)", fontsize=10)
axs[1].set_ylabel("Current (A)", fontsize=10)
axs[1].legend(fontsize=9, loc="upper right")
axs[1].grid(True, linestyle="--", linewidth=0.5, alpha=0.7)

# Adjust spacing to prevent overlap
plt.tight_layout()
plt.show()
