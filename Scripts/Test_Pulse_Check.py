from B1500.B1500Unified import B1500
import numpy as np
import matplotlib.pyplot as plt
import time

#What if we had a program that simply biased the Gate and then every 5 minutes it checks the Conductance of the drain and spits out what happens
#So I can make a program that automatically goes through each voltage and checks and waits until the conductance levels off so I can see change 
#in confuctance versus voltage and how long it takes to program each state for each voltage cause what if lower conductance/Higher voltage states
#are arived at faster compared to the change in conductance


#So what if we had the core methods set up in a way that we could designate in our parameters that we have our SMUs set up as like Drain = 4, Source = 3, Gate, Base
# and then when we run the core SMU functions we designate like test pad = "Drain" and if we designate multiple pads then we do a simultaneous measurement like 
# if len(pads) > 1 then do this code chunk instead of the usual single pad measurement

#What if we turned the bias_smu function and made a new one called Bias SMus and it looks for my SMU config and SMU Bias numbers and maybe a SMU Bias 1 or SMU Bias 2 identifier
# to allow for multiple bias steps

#lets make it so you just pass the b1500 object, your test pad identifier and maybe other identifiers like bias pads. to each method and it pulls out your test parameters 
# and we can make them all have specific inputs that we make available to the user they can input them as they pelase and it shows the default and the user simply just fills
# them out. What if the parameters had to be listed in order and once we grab some parameters we can assume them used and grab the next set for each method

#What if each method we don't ask for anything but the b1500 object and the test pad and everything else like other bias is put into parameters so list your methods and 
# fill them with b1500 and testpad = "Drain"
# Then the parameters window is where we set all the little details so like other pads and their bias and assume if not listed at frist part where "drain" = 4 then its not in use
# but if it is in use and not bias was defined then assume to be grounded
# other parameters like interval would be set and we could have a structure like follows:

#after name test and whatnot require parameters

#SMU Config
#   "Drain" = 4,

#IVSweep
#   "Voltage Start" = 0,
#   "Voltage Stop" = 1,
#   "Drain Bias" = 1, # This would set the bias during the sweep to whatever smu was plugged into the drain

#Initial Conductance #Since we use this so much we should have an initial conductance method that grabs conductance and time and return a solid value
#   "Drain Bias" = 1,

#What about loops will the execution happen out of order what if we branch back to the top?
#Could we just label our different method calls with a distinct Name like 4termincal spot read and then a number or identifier between them 
# and how would we group the values in them?

# Define experiment parameters
parameters = {
    "Name": "Evan",
    "Test Number": "ask",
    "Die Number": 1,
    "Device Number": 67,
    "Waveform Format": "Reram",  # Loads "Reram.txt"
    "Waveform": "Evan_Reram_4",

    #SMU Configuration
    "Drain": 4, #SMU4 is connected to the drain
    "Source": 3,
    "Gate": 2,
    "Base": 1,

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


b1500.smu.IVSweep(b1500.Drain, vstart=b1500.v_rd, vstop=b1500.Stop , nsteps=b1500.Steps, mode=b1500.Mode, icomp=b1500.ICompliance, connect_first=True, disconnect_after=True , plot_data=True)

#Next get Initial Conductance:
read_initial = B1500.smu.smu_meas_spot_4termininal(smu_numD=4, smu_numG=1, smu_numS=3, smu_numB=2, VDbias = b1500.v_rd, VGbias = 0,VSbias = 0, VBbias = 0 , vmeas=0.1 , icomp=100e-3 , reset_timer=True , disconnect_after=True )
current_initial = read_initial[2]
time_initial = read_initial[0]
cond_initial = current_initial/1 
g_d = cond_initial
print(f"\nTHE INITIAL CONDUCTANCE IS: {g_d*1e9}nS")

initial_run  = True #flag so I can do fast looping
last_run = False
GLEVEL = False
g_d_new = 0

#Now lets loop between Setting a DC Bias on the gate and Reading the conductance after a certain time
while not GLEVEL: #am I leveled off or saturated conductance

    if last_run: #am I done? if yes then disconnect all SMUS
        b1500.smu.disconnect_smu_list([1, 2, 3, 4]) #Hey Clean this up Later
        break

    g_d = g_d_new

    #Bias Just the Gate and leave everything else at 0
    b1500.smu.bias_smu(b1500.Drain, b1500.Drain_Bias, Icomp=100e-3)
    b1500.smu.bias_smu(b1500.Gate, b1500.Gate_Bias, Icomp=100e-3)
    b1500.smu.bias_smu(b1500.Source, b1500.Source_Bias, Icomp=100e-3)
    b1500.smu.bias_smu(b1500.Base, b1500.Base_Bias, Icomp=100e-3)

    #Wait for a certain amount of time
    print(f"Waiting for {b1500.Wait} seconds")
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
    read_initial = B1500.smu.smu_meas_spot_4termininal(smu_numD=4, smu_numG=1, smu_numS=3, smu_numB=2, VDbias = b1500.v_rd, VGbias = 0,VSbias = 0, VBbias = 0 , vmeas=0.1 , icomp=100e-3 , reset_timer=True , disconnect_after=disconnect_after, clear_settings = True, activate_smus = activate_smus)
    current_initial = read_initial[2]
    time_initial = read_initial[0]
    cond_initial = current_initial/1 
    g_d_new = cond_initial

    #Check if conductance has leveled off
    if ((g_d_new > (g_d - b1500.test_info.g_min_tolerance)) & (g_d_new < (g_d + b1500.test_info.g_max_tolerance))):
        GLEVEL = True
        last_run = True

print(f"My Voltage: {b1500.test_info.Gate_Bias}V Gives me a Conductance of: {g_d_new}S")
