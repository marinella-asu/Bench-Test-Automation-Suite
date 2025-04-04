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
    "Test Number": "3090",
    "Die Number": 1,
    "Device Number": 53,
    "Waveform Format": "Reram",  # Loads "Reram.txt"
    "Waveform": "Evan_Reram_4",
    "Filename": "Read-Test-Cond-DV-GV",
    
    #Heres my probe setup
    "smu_numD": 4,
    "smu_numG": 1,
    "smu_numS": 2,
    "smu_numB": 3,
    
    #Read Voltage Modifications
    "SubDivisions": 10, #Minimum value of 1
    "MaxDrainV": 1,
    "MaxGateV": -3
}

# Initialize Unified B1500 (includes parameter validation)
b1500 = B1500(unit_label = 'A', parameters=parameters)

#Instantiate empty dataframe for storing my in progress data
all_data = np.empty((0, 3))

#Flag for only having to connect SMUs once
ActivateSmusFlag = True

g_d = 0

try:
    # Initialize empty data storage
    all_data = np.empty((0, 3))  # Columns: Conductance, Drain V, Gate V
    
    for i in range(1, b1500.SubDivisions):
        # Get next Gate Voltage
        nextGateVoltage = i * (b1500.MaxGateV / b1500.SubDivisions)
        for _ in range(10):
            read_initial = b1500.smu.smu_meas_spot_4terminal(
                b1500.smu_numD, b1500.smu_numG, b1500.smu_numS, b1500.smu_numB,
                VDbias=b1500.MaxDrainV, VGbias=nextGateVoltage, VSbias=0, VBbias=0,
                vmeas=0.1, icomp=100e-3, reset_timer=True, disconnect_after=False,
                activate_smus=ActivateSmusFlag
            )
            ActivateSmusFlag = False  # Only activate once
            
            # Process and clean data
            data = b1500.data_clean(b1500, read_initial, parameters, NoSave=True)
            time_drain = data.get("SMU4_Time", None)
            current_drain = data.get("SMU4_Current", None)

            # Compute conductance
            current_initial = float(current_drain[0])
            cond_initial = current_initial / b1500.MaxDrainV
            g_d += cond_initial
        
        # # **Rise: Sweep Drain Voltage Up**
        # for j in range(1, b1500.SubDivisions):
        #     nextDrainVoltage = j * (b1500.MaxDrainV / b1500.SubDivisions)
            
        #     # Measure Conductance
        #     g_d = 0
        #     for _ in range(10):
        #         read_initial = b1500.smu.smu_meas_spot_4terminal(
        #             b1500.smu_numD, b1500.smu_numG, b1500.smu_numS, b1500.smu_numB,
        #             VDbias=nextDrainVoltage, VGbias=nextGateVoltage, VSbias=0, VBbias=0,
        #             vmeas=0.1, icomp=100e-3, reset_timer=True, disconnect_after=False,
        #             activate_smus=ActivateSmusFlag
        #         )
        #         ActivateSmusFlag = False  # Only activate once
                
        #         # Process and clean data
        #         data = b1500.data_clean(b1500, read_initial, parameters, NoSave=True)
        #         time_drain = data.get("SMU4_Time", None)
        #         current_drain = data.get("SMU4_Current", None)
    
        #         # Compute conductance
        #         current_initial = float(current_drain[0])
        #         cond_initial = current_initial / nextDrainVoltage
        #         g_d += cond_initial
            
        # Store averaged conductance
        averaged_g = g_d / 10
        new_data = [averaged_g, b1500.MaxDrainV, nextGateVoltage]
        all_data = np.append(all_data, [new_data], axis=0)
    
        # # **Fall: Sweep Drain Voltage Down**
        # for j in range(b1500.SubDivisions - 1, 0, -1):
        #     nextDrainVoltage = j * (b1500.MaxDrainV / b1500.SubDivisions)
    
        #     # Measure Conductance
        #     g_d = 0
        #     for _ in range(10):
        #         read_initial = b1500.smu.smu_meas_spot_4terminal(
        #             b1500.smu_numD, b1500.smu_numG, b1500.smu_numS, b1500.smu_numB,
        #             VDbias=nextDrainVoltage, VGbias=nextGateVoltage, VSbias=0, VBbias=0,
        #             vmeas=0.1, icomp=100e-3, reset_timer=True, disconnect_after=False,
        #             activate_smus=ActivateSmusFlag
        #         )
        #         ActivateSmusFlag = False  # Only activate once
                
        #         # Process and clean data
        #         data = b1500.data_clean(b1500, read_initial, parameters, NoSave=True)
        #         time_drain = data.get("SMU4_Time", None)
        #         current_drain = data.get("SMU4_Current", None)
    
        #         # Compute conductance
        #         current_initial = float(current_drain[0])
        #         cond_initial = current_initial / nextDrainVoltage
        #         g_d += cond_initial
            
        #     # Store averaged conductance
        #     averaged_g = g_d / 10
        #     new_data = [averaged_g, nextDrainVoltage, nextGateVoltage]
        #     all_data = np.append(all_data, [new_data], axis=0)


    #Close SMUs and Save Data
    b1500.connection.write("CL")
    b1500.save_numpy_to_csv(b1500.test_info, all_data, filename = b1500.Filename)
except KeyboardInterrupt:
    print("Keyboard Interrupt detected. Saving the data...")
    #Close SMUs and Save Data
    b1500.connection.write("CL")
    b1500.save_numpy_to_csv(b1500.test_info, all_data, filename = f"{b1500.Filename}-Stopped")
    