from B1500.B1500Unified import B1500
import numpy as np
import matplotlib.pyplot as plt
import time

# Define experiment parameters
parameters = {
    "Name": "Evan",
    "Test Number": 1,
    "Die Number": 1,
    "Device Number": 67,

    "Waveform Format": "Reram",  # Loads "Reram.txt"
    "Waveform": "ReRam_Program_Evan", #Set this to Load a Waveform into the Editor
    "Waveform Editor": "ask",   #Uncomment this to load the waveform editor
    "VDD WGFMU": 1,
    "VSS WGFMU": 2,
    "trd": 1e-4,
    "pts_per_meas" : 1,
    
    "Short_Check_Test": { #Must have "_" instead of " "
        "SMU_Pair": [2, 3], #Measure 1 Ground 2
        "Max_Resistance": 200, #200 Ohms or less is a short
        "Max_Voltage": .1, #Max Voltage We can use
        "IComp": 100e-3,
        "Dynamic_Check": True, #Do an aautomatic Ramp
        "D_StartV": .1,
        "D_Step": 1, #Step of .5V each time we elapse D_Wait
        "D_Wait": 10,
        "SaveData": True
    },
    
    #Check For a Short between two SMUS this is a contact measurement
    "Form_Test": { #Must have "_" instead of " "
        "SMU_Pair": [1, 2], #Measure 1 Ground 2
        "Max_Resistance": 10000, #200 Ohms or less is a short
        "Max_Voltage": 7, #Max Voltage We can use
        "IComp": 1e-3,
        "Dynamic_Check": True, #Do an aautomatic Ramp
        "D_StartV": 3,
        "D_Step": .1, #Step of .5V each time we elapse D_Wait
        "D_Wait": 2,
        "SaveData": True,
        "Reset_Voltage": -1,
        "Reset_Compliance": 100e-3
    },

    "Switch_Test": {
        "SMU_Pair": [1,2],
        "num_loops": 2,
        "Read_Voltage": .1,
        "Pos_Voltage": 2,
        "Neg_Voltage": -1,
        "VStep": .05,
        "ICompSet": 1e-3, #Add in different positive versus negative compliance
        "ICompReset": 100e-3,
        "ICompRead": 100e-3,
        "SaveData": True,
        "Reset_Voltage_Step": .1
    },

    "Program": {
        "min_gtarget": .00095,   # ‑‑ Lowest Conductance Target
        "max_gtarget": .001,  # ‑‑ Highest Conductance Target
        "num_level":   2,        # ‑‑ How many levels in between those levels do we want to program to
        "num":         20,       # ‑‑ How many times we hold a programming voltage before increasing intensity
        "num_reads":   10,       # ‑‑ How many times we read the device during validation to verify we did program the correct state
        "v_rd":        0.1,      # ‑‑ Read Voltage during validation and RTN
        "v_prg":       1,      # ‑‑ Initial Set Voltage for programming
        "v_rst":       -1,      # -- Initial Reset Voltage for programming
        "v_prg_max":   2.3,      # ‑‑ Maximum value used for Set operation
        "v_count":     0,        # (initial counter)
        "v_countmax":  1000,       # ‑‑ Maximum times we'll try to program and validate before giving up on the state 
        "goffset":     1e-6, #Validation Range +- offset 
        "ProgramTargetOffset": 10e-6, #+- offset around our programmed states (How close do we need to be to our set state to be correct)
        "read_waveform": "ReRam_Read_Evan", #Waveform used during read operation
        "program_waveform": "ReRam_Program_Evan", #Waveform used during Program operation
        "RTN_waveform":     "ReRam_RTN_Evan", #Waveform used during RTN read operation
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

b1500.connection.write("CL")
b1500.wgfmu.wg.WGFMU_clear()




