from B1500.B1500Unified import B1500
import numpy as np
import matplotlib.pyplot as plt

#What if we had a program that simply biased the Gate and then every 5 minutes it checks the Conductance of the drain and spits out what happens
#So I can make a program that automatically goes through each voltage and checks and waits until the conductance levels off so I can see change 
#in confuctance versus voltage and how long it takes to program each state for each voltage cause what if lower conductance/Higher voltage states
#are arived at faster compared to the change in conductance

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

#This is my probe setup
smu_numD = 1
smu_numG = 4
smu_numS = 3
smu_numB = 2

#First Form device:
B1500.smu.IVSweep(smu_numD, vstart=VSTART , vstop=VSTOP , nsteps=NSTEPS , mode=mode, icomp=ICOMP, connect_first=True, disconnect_after=True , plot_data=True)

#Next get Initial Conductance:
read_initial = B1500.smu.smu_meas_spot_4termininal(smu_numD=4, smu_numG=1, smu_numS=3, smu_numB=2, VDbias = v_rd, VGbias = 0,VSbias = 0, VBbias = 0 , vmeas=0.1 , icomp=100e-3 , reset_timer=True , disconnect_after=True )
current_initial = read_initial[2]
time_initial = read_initial[0]
cond_initial = current_initial/1 
g_d = cond_initial
print(f"\nTHE INITIAL CONDUCTANCE IS: {g_d*1e9}nS")

#These are the Targets I want to reach and cycle through to see what programmed states I can reach
gtargets = np.linspace(min_gtarget, max_gtarget, num=STEP)

#Go through each target
for i, gtarget in enumerate(gtargets):

    print(f"\n\nTHE TARGET CONDUCTANCE IS:{gtarget*1e9}nS\n\n\n")
    g_min = gtarget - 0.25e-9 #This is my range of values Ill accept for my target
    g_max = gtarget + 0.75e-9

    while not correct_program: #Have I reached the Target range?

        if abs(v_prg)>19 or abs(v_rst)>16: #Stop If I have to use to high of a programming voltage
            print("Max Program Voltage Reached. Stopping...")
            sys.exit()

        if g_cur >= g_max: #Am I Programmed too High?
            print("\nIn the Erasing loop.\n")
            v_rst = v_rst - vstep
            results = B1500.smu.smu_meas_sample_multi_term( smu_numD = 1, 
                                                    smu_numG = 2, 
                                                    smu_numS = 3, 
                                                    smu_numB = 4, 
                                                    vmeasD=0,
                                                    vmeasG=v_rst,
                                                    vmeasS=0, 
                                                    vmeasB=0,
                                                    icompDSB=100e-3, 
                                                    icompG=0.1,  
                                                    interval=t_prg, 
                                                    pre_bias_time=0, 
                                                    number=2, 
                                                    disconnect_after=False, 
                                                    plot_results=False )
            
            print(f'Measurement results of Program: {results}')
            read_verify = B1500.smu.smu_meas_spot_4termininal(smu_numD=4, smu_numG=1, smu_numS=3, smu_numB=2,VDbias = v_rd, VGbias = 0,VSbias = 0, VBbias = 0 , vmeas=0.1 , icomp=100e-3 , reset_timer=True , disconnect_after=True )
            print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n')
            print(f'Spot meas Current: {current_initial}')
            current_initial = read_verify[2]
            time_initial = read_verify[0]
            g_cur = current_initial/1
            print(f"\nThe state of the program is at {g_cur*1e9}nS, Target is [{g_min*1e9}nS, {g_max*1e9}nS], with applied voltage of {v_rst}V with condition [{done}]\n\n")
            pulse_num += 1
            pulse_data.append([v_rst, g_cur[0] if isinstance(g_cur, (list, np.ndarray)) else g_cur])  # Store conductance as scalar

results_read = b1500.smu.smu_meas_sample_multi_term( smu_numD = smu_numD, 
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
                                    plot_results=False)

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
