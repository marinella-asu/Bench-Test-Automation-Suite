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
    
    "Form_Test": {
        "SMU_Pair": [1, 2],  #This is the list of the two SMUs well use in this order [measured, ground] 
        "Max_Resistance": 10000, #This is the maximum resistance device we will consider to be formed (Usually set by the complaiance current and the current voltage during forming)
        "Max_Voltage": 7, #Max Voltage We can use before turning off the test
        "IComp": 1e-3, #Compliance limit used during the forming operation
        "Dynamic_Check": True, #This sets the operation to do a staircase sweep instead of holding a continuous voltage value
        "D_StartV": 1, #Starting voltage for the sweep (only used if we are doing a dynamic sweep)
        "D_Step": .1, #Voltage step increased after D_Wait seconds (only used if we are doing a dynamic sweep)
        "D_Wait": 2, #Wait time per each voltage in seconds (only used if we are doing a dynamic sweep)
        "Reset_Voltage": .1, #This is the reset voltage used after the device is successfully formed so we can start future tests with each device in its reset state
        "Reset_Compliance": 100e-3, #This is the compliance used during the reset sweep after forming
        "SaveData": True,  #Save the data to csv?

    },
    
}

# Initialize Unified B1500 (includes parameter validation)
b1500 = B1500(unit_label = 'A', parameters=parameters)


didItForm = b1500.smu.Forming(b1500, "Form_Test")
print(f"We Formed the Device?: {didItForm}")

b1500.connection.write("CL") #Used to make absolutely sure the B1500 and WGFMU are set to a default safe state upon program exit
b1500.wgfmu.wg.WGFMU_clear()