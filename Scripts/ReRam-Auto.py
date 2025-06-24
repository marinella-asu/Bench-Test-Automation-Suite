from B1500.B1500Unified import B1500
import numpy as np
import matplotlib.pyplot as plt
import time

# Define experiment parameters
parameters = {
    "Name": "Evan", #These parameters must be changed by the experimenter for better data filing and collection and determines where your data is stored and what it's name is stored as
    "Sample_ID": "Batch3_F5_TPTE33",

    "Waveform Format": "Reram",  # Loads a waveform format (Used in unfinished Waveform creation GUI disregard for now)
    "Waveform": "ReRam_Program_Evan", #Set this to Load a Waveform into the Editor
    # "Waveform Editor": "ask",   #Uncomment this to load the waveform editor on program runtime
    "VDD WGFMU": 1, #This sets what channel of the WGFMU the VDD waveform is applied to
    "VSS WGFMU": 2, #This sets what channel of the WGFMU the VSS waveform is applied to
    "trd": 1e-4, #Used during WGFMU waveform generation
    "pts_per_meas" : 1, #Used during WGFMU waveform generation
    
    "Short_Check_Test": { 
        "SMU_Pair": [1, 2], #This is the list of the two SMUs well use in this order [measured, ground] 
        "Max_Resistance": 200, #This is the maximum resistance we would consider to be a short between two probe tips
        "Max_Voltage": .1, #Max Voltage We can use to test if both probes are shorted
        "IComp": 100e-3, #Compliance limit used during the test
        "Dynamic_Check": True, ##This sets the operation to do a staircase sweep instead of holding a continuous voltage value
        "D_StartV": .1, #Starting voltage for the sweep (only used if we are doing a dynamic sweep)
        "D_Step": 1, #Voltage step increased after D_Wait seconds (only used if we are doing a dynamic sweep)
        "D_Wait": 10, #Wait time per each voltage in seconds (only used if we are doing a dynamic sweep)
        "SaveData": True #Save the data to csv?
    },
    
    #Check For a Short between two SMUS this is a contact measurement
    "Form_Test": {
        "SMU_Pair": [1, 2],  #This is the list of the two SMUs well use in this order [measured, ground] 
        "Max_Resistance": 10000, #This is the maximum resistance device we will consider to be formed (Usually set by the complaiance current and the current voltage during forming)
        "Max_Voltage": 7, #Max Voltage We can use before turning off the test
        "IComp": 1e-3, #Compliance limit used during the forming operation
        "Dynamic_Check": True, #This sets the operation to do a staircase sweep instead of holding a continuous voltage value
        "D_StartV": 1, #Starting voltage for the sweep (only used if we are doing a dynamic sweep)
        "D_Step": .1, #Voltage step increased after D_Wait seconds (only used if we are doing a dynamic sweep)
        "D_Wait": 2, #Wait time per each voltage in seconds (only used if we are doing a dynamic sweep)
        "Reset_Voltage": -1.5, #This is the reset voltage used after the device is successfully formed so we can start future tests with each device in its reset state
        "Reset_Compliance": 100e-3, #This is the compliance used during the reset sweep after forming
        "SaveData": True,  #Save the data to csv?

    },

    "Switch_Test": {
        "SMU_Pair": [1,2], #This is the list of the two SMUs well use in this order [measured, ground] 
        "num_loops": 5, #This is how many set-reset loops the code will run through
        "Read_Voltage": .1, #This is votlage the device will  be read at for testing the conductance level and comparing our memory windows
        "Pos_Voltage": 2.3, #This is the maximum positive voltage that the device will be swept to during the set operation
        "Neg_Voltage": -1, #This is the starting voltage the device will be swept to during reset (This increments if our memory window is not large enough >MinMemWindow)
        "Min_MemWindow": 1.1,
        "Reset_Voltage_Step": .1, #This is the step by which the reset voltage will decrease by every loop where we do not see a substantial change between set and reset
        "ICompSet": 1e-3, #This is the compliance used during the set operation sweep
        "ICompReset": 100e-3, #This is the compliance used during the reset operation sweep
        "ICompRead": 100e-3, #This is the compliance limit used during the read of the device
        "SaveData": True, #Save the data to csv?
    },

    "Program": {
        "min_gtarget": .0002,   # ‑‑ Lowest Conductance Target
        "max_gtarget": .0013,  # ‑‑ Highest Conductance Target
        "num_level":   12,        # ‑‑ How many levels in between those levels do we want to program to
        "num":         20,       # ‑‑ How many times we hold a programming voltage before increasing intensity
        "num_reads":   10,       # ‑‑ How many times we read the device during validation to verify we did program the correct state
        "v_rd":        0.1,      # ‑‑ Read Voltage during validation and RTN
        "v_prg":       .7,      # ‑‑ Initial Set Voltage for programming
        "v_rst":       -.8,      # -- Initial Reset Voltage for programming
        "v_prg_max":   10,      # ‑‑ Maximum value used for Set operation
        "v_countmax":  1000,       # ‑‑ Maximum times we'll try to program and validate before giving up on the state 
        "v_count":     0,        # initial state of counter for how many times we'll try to program and validate before giving up on the state 
        "goffset":     5e-6, #Validation Range +- offset 
        "ProgramTargetOffset": 5e-6, #+- offset around our programmed states (How close do we need to be to our set state to be considered programmed and begin trying to validate the state)
        "read_waveform": "ReRam_Read_Evan", #Waveform used during read operation
        "program_waveform": "ReRam_Program_Evan", #Waveform used during Program operation
        "RTN_waveform":     "Retention_10Min", #Waveform used during RTN read operation
    },

    "SmartProgram": {
        "min_gtarget": .000200,   # ‑‑ Lowest Conductance Target
        "max_gtarget": .001300,  # ‑‑ Highest Conductance Target
        "num_level":   6,        # ‑‑ How many levels in between those levels do we want to program to
        "num":         20,       # ‑‑ How many times we hold a programming voltage before increasing intensity
        "num_reads":   10,       # ‑‑ How many times we read the device during validation to verify we did program the correct state
        "v_rd":        0.1,      # ‑‑ Read Voltage during validation and RTN
        "v_prg":       1,      # ‑‑ Initial Set Voltage for programming
        "v_rst":       -1,      # -- Initial Reset Voltage for programming
        "v_prg_max":   2.3,      # ‑‑ Maximum value used for Set operation
        "v_countmax":  1000,       # ‑‑ Maximum times we'll try to program and validate before giving up on the state 
        "v_count":     0,        # initial state of counter for how many times we'll try to program and validate before giving up on the state 
        "goffset":     5e-6, #Validation Range +- offset 
        "ProgramTargetOffset": 10e-6, #+- offset around our programmed states (How close do we need to be to our set state to be considered programmed and begin trying to validate the state)
        "read_waveform": "ReRam_Read_Evan", #Waveform used during read operation
        "program_waveform": "ReRam_Program_Evan", #Waveform used during Program operation
        "RTN_waveform":     "ReRam_RTN_Evan", #Waveform used during RTN read operation
        "boundary_super_coarse" : 100e-6,
        "boundary_coarse" : 50e-6,
        "boundary_fine" : 50e-6,
        "boundary_ultra_fine" : 0.5e-6,
        "super_coarse_step" : 100e-6,
        "coarse_step" : 25e-6,
        "fine_step" : 25e-6,
        "ultra_fine_step" : 0.5e-6,
        "ultra_ultra_fine_step" : 0.5e-6,
        "use_super_coarse" : False,
        "use_fine" : False,
        "use_ultra_fine" : False,
        "use_ultra_ultra_fine" : False,
    },

    "Retention":{
        "SMU_Pair": [1,2],
        "ReadVoltage": .1,
        "ReadCompliance": 100e-3,
        "Interval": 10e-3,
        "Duration": 180,
        "SampleRate": 2,
        "SaveData": True,
    }


    
}

# Initialize Unified B1500 (includes parameter validation)
b1500 = B1500(unit_label = 'A', parameters=parameters)

# didItShort = b1500.smu.Short_Check(b1500, "Short_Check_Test")
# print(f"We were able to short the two pads?: {didItShort}")

# didItForm = b1500.smu.Forming(b1500, "Form_Test")
# print(f"We Formed the Device?: {didItForm}")

# didweSwitch = b1500.smu.Switch_Test(b1500, "Switch_Test")
# print(f"Did we successfully switch through all the loops?: {didweSwitch}")

didweProgram = b1500.wgfmu.ProgramAndRTN(b1500, "Program")
print(f"Did we successfully Program?: {didweProgram}")

# didweSmartProgram = b1500.wgfmu.SmartProgramAndRTN(b1500, "SmartProgram")
# print(f"Did we successfully Program?: {didweSmartProgram}")

# didweRetention = b1500.smu.ReRamRetention(b1500, "Retention")
# print(f"Did we successfully Retention?: {didweRetention}")

b1500.connection.write("CL") #Used to make absolutely sure the B1500 and WGFMU are set to a default safe state upon program exit
b1500.wgfmu.wg.WGFMU_clear()




