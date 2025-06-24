from B1500.B1500Unified import B1500
import numpy as np
import matplotlib.pyplot as plt
import time

parameters = {
    "Name": "Evan", #These parameters must be changed by the experimenter for better data filing and collection and determines where your data is stored and what it's name is stored as
    "Sample_ID": "Batch3_F5_TPTE16",

    "Waveform Format": "Reram",  # Loads a waveform format (Used in unfinished Waveform creation GUI disregard for now)
    "Waveform": "ReRam_Program_Evan", #Set this to Load a Waveform into the Editor
    # "Waveform Editor": "ask",   #Uncomment this to load the waveform editor on program runtime
    "VDD WGFMU": 1, #This sets what channel of the WGFMU the VDD waveform is applied to
    "VSS WGFMU": 2, #This sets what channel of the WGFMU the VSS waveform is applied to
    "trd": 1e-4, #Used during WGFMU waveform generation
    "pts_per_meas" : 1, #Used during WGFMU waveform generation
    
    "Switch_Test": {
        "SMU_Pair": [1, 2], #This is the list of the two SMUs well use in this order [measured, ground] 
        "num_loops": 3, #This is how many set-reset loops the code will run through
        "Read_Voltage": .1, #This is votlage the device will  be read at for testing the conductance level and comparing our memory windows
        "Pos_Voltage": 2, #This is the maximum positive voltage that the device will be swept to during the set operation
        "Neg_Voltage": -4, #This is the starting voltage the device will be swept to during reset (This increments if our memory window is not large enough >MinMemWindow)
        "Min_MemWindow": 1.1,
        "Reset_Voltage_Step": .1, #This is the step by which the reset voltage will decrease by every loop where we do not see a substantial change between set and reset
        "ICompSet": 3e-3, #This is the compliance used during the set operation sweep
        "ICompReset": 100e-3, #This is the compliance used during the reset operation sweep
        "ICompRead": 100e-3, #This is the compliance limit used during the read of the device
        "SaveData": True, #Save the data to csv?
    },

}

# Initialize Unified B1500 (includes parameter validation)
b1500 = B1500(unit_label = 'A', parameters=parameters)

didweSwitch = b1500.smu.Switch_Test(b1500, "Switch_Test")
print(f"Did we successfully switch through all the loops?: {didweSwitch}")

b1500.connection.write("CL") #Used to make absolutely sure the B1500 and WGFMU are set to a default safe state upon program exit
b1500.wgfmu.wg.WGFMU_clear()