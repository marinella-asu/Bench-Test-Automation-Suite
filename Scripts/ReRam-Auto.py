from B1500.B1500Unified import B1500
import numpy as np
import matplotlib.pyplot as plt
import time

# Define experiment parameters
parameters = {
    "Name": "Evan",
    "Test Number": 800,
    "Die Number": 1,
    "Device Number": 67,
    "Waveform Format": "Reram",  # Loads "Reram.txt"
    "Waveform": "Evan_Reram_4",

    # "Waveform Editor": "ask",   
    "VDD WGFMU": 1,
    "VSS WGFMU": 2,
    "Interval": 1.5e-3,
    "data points": 300,
    
    "Short_Check_Test": { #Must have "_" instead of " "
        "SMU_Pair": [3, 4], #Measure 1 Ground 2
        "Max_Resistance": 200, #200 Ohms or less is a short
        "Max_Voltage": 5, #Max Voltage We can use
        "Dynamic_Check": True, #Do an aautomatic Ramp
        "D_StartV": 0,
        "D_Step": .5, #Step of .5V each time we elapse D_Wait
        "D_Wait": 10,
        "SaveData": True
    },
    
    #Check For a Short between two SMUS this is a contact measurement
    "Form_Test": { #Must have "_" instead of " "
        "SMU_Pair": [4, 3], #Measure 1 Ground 2
        "Max_Resistance": 900, #200 Ohms or less is a short
        "Max_Voltage": 5, #Max Voltage We can use
        "Dynamic_Check": True, #Do an aautomatic Ramp
        "D_StartV": 1,
        "D_Step": .1, #Step of .5V each time we elapse D_Wait
        "D_Wait": 10,
        "SaveData": True
    },

    "Switch_Test": {
        "SMU_Pair": [1,2],
        "num_loops": 10,
        "Read_Voltage": 1,
        "Max_Pos_Voltage": 12,
        "Max_Neg_Voltage": -10,
        "VStep": .1,
        "IComp": 100e-3,
        "SaveData": True
    },

    "Program": {
        "min_gtarget": 300e-6,   # ‑‑ G_Minimum_Target
        "max_gtarget": 1000e-6,  # ‑‑ G_Maximum_Target
        "num_level":   7,        # ‑‑ Num_Levels
        "num":         30,       # ‑‑ Prog_Num
        "num_reads":   10,       # ‑‑ Prog_Num_Reads
        "v_rd":        0.1,      # ‑‑ V_Read
        "v_prg":       1.0,      # ‑‑ V_Prog_Start
        "vstop":       0.0,      # ‑‑ V_Stop
        "v_prg_max":   9.8,      # ‑‑ V_Prog_Max
        "v_count":     0,        # (initial counter)
        "v_countmax":  40,       # ‑‑ V_Count_Max
        "goffset":     1e-6
    }
    
    

    
}

# Initialize Unified B1500 (includes parameter validation)
b1500 = B1500(unit_label = 'A', parameters=parameters)

# didItShort = b1500.smu.Short_Check(b1500, "Short_Check_Test")
# print(f"We were able to short the back gate?: {didItShort}")

# didItForm = b1500.smu.Short_Check(b1500, "Form_Test")
# print(f"We Formed the Device?: {didItForm}")

# didweSwitch = b1500.smu.Switching_Test(b1500, "Switch_Test")
# print(f"Did we successfully switch through all the loops?: {didweSwitch}")

didweProgram = b1500.wgfmu.ProgramAndRTN(b1500, "Program")
print(f"Did we successfully Program?: {didweProgram}")



