from B1500.B1500Unified import B1500
import numpy as np
import matplotlib.pyplot as plt
import time

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

    #Device Read Values
    "v rd": 1,
    "Wait": 2e-3, #in seconds
    "g min tolerance": 0.25e-9, #Change These
    "g max tolerance": 0.75e-9,  #Change These

    #Bias Values for Programming
    "Gate Bias": 4,
    "Drain Bias": 0,
    "Source Bias": 0,
    "Base Bias": 0,

    #Initial Sweep Values
    "Start": 0,
    "Stop": 1,
    "Steps": 101,
    "Mode": 3, #Double Sweep Change to 1 for single
    "ICompliance": .1
}

# Initialize Unified B1500 (includes parameter validation)
b1500 = B1500(unit_label = 'A', parameters=parameters)

#This is my probe setup I think (only matters for biasing my device)
smu_numD = 4
smu_numG = 2
smu_numS = 3
smu_numB = 1


b1500.smu.IVSweep(smu_numD, vstart=b1500.test_info.Start, vstop=b1500.test_info.Stop , nsteps=b1500.test_info.Steps, mode=b1500.test_info.Mode, icomp=b1500.test_info.ICompliance, connect_first=True, disconnect_after=True , plot_data=True)

#Next get Initial Conductance:
read_initial = B1500.smu.smu_meas_spot_4termininal(smu_numD=4, smu_numG=1, smu_numS=3, smu_numB=2, VDbias = b1500.test_info.v_rd, VGbias = 0,VSbias = 0, VBbias = 0 , vmeas=0.1 , icomp=100e-3 , reset_timer=True , disconnect_after=True )
current_initial = read_initial[2]
time_initial = read_initial[0]
cond_initial = current_initial/1 
g_d = cond_initial
print(f"\nTHE INITIAL CONDUCTANCE IS: {g_d*1e9}nS")

initial_run  = True #flag so I can do fast looping
last_run = False
GLEVEL = False
<<<<<<< HEAD
=======
g_d_new = 0
>>>>>>> 1e29eaeee6f5e2c3137cf017ecfe796e5e992612

#Now lets loop between Setting a DC Bias on the gate and Reading the conductance after a certain time
while not GLEVEL: #am I leveled off or saturated conductance

    if last_run: #am I done? if yes then disconnect all SMUS
        b1500.smu.disconnect_smu_list([1, 2, 3, 4]) #Hey Clean this up Later
        break

    g_d = g_d_new
    #Bias Just the Gate and leave everything else at 0
    b1500.smu.bias_smu(smu_numD, b1500.test_info.Drain_Bias, Icomp=100e-3)
    b1500.smu.bias_smu(smu_numG, b1500.test_info.Gate_Bias, Icomp=100e-3)
    b1500.smu.bias_smu(smu_numS, b1500.test_info.Source_Bias, Icomp=100e-3)
    b1500.smu.bias_smu(smu_numB, b1500.test_info.Base_Bias, Icomp=100e-3)

    #Wait for a certain amount of time
    print(f"Waiting for {b1500.test_info.Wait} seconds")
    time.sleep(b1500.test_info.Wait)  # Pauses execution for a variable number of seconds
    print("Done waiting!")

    
    if initial_run: #check for fast looping
        activate_smus = True
        disconnect_after = False
    else:
        activate_smus = False

    if last_run: #Not really needed since we break on last run earlier
        disconnect_after = True

    #Get my conductance after biasing the Gate for so long
    read_initial = B1500.smu.smu_meas_spot_4termininal(smu_numD=4, smu_numG=1, smu_numS=3, smu_numB=2, VDbias = b1500.test_info.v_rd, VGbias = 0,VSbias = 0, VBbias = 0 , vmeas=0.1 , icomp=100e-3 , reset_timer=True , disconnect_after=disconnect_after, clear_settings = True, activate_smus = activate_smus)
    current_initial = read_initial[2]
    time_initial = read_initial[0]
    cond_initial = current_initial/1 
    g_d_new = cond_initial

    #Check if conductance has leveled off
    if ((g_d_new > (g_d - b1500.test_info.g_min_tolerance)) & (g_d_new < (g_d + b1500.test_info.g_max_tolerance))):
        GLEVEL = True
        last_run = True

print(f"My Voltage: {b1500.test_info.Gate_Bias}V Gives me a Conductance of: {g_d_new}S")
