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
    "Waveform": "Evan_Reram_3",
    # "Waveform Editor": "ask",  
    "VDD WGFMU": 1,
    "VSS WGFMU": 2,
    "trd": 1e-4,
    "pts_per_meas" : 1,
    
    "Short_Check_Test": { #Must have "_" instead of " "
        "SMU_Pair": [1, 2], #Measure 1 Ground 2
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
        "D_StartV": 1,
        "D_Step": .5, #Step of .5V each time we elapse D_Wait
        "D_Wait": 2,
        "SaveData": True,
        "Reset_Voltage": -1,
        "Reset_Compliance": 100e-3
    },

    "Switch_Test": {
        "SMU_Pair": [1,2],
        "num_loops": 2,
        "Read_Voltage": .1,
        "Max_Pos_Voltage": 2,
        "Max_Neg_Voltage": -1,
        "VStep": .05,
        "ICompSet": 1e-3, #Add in different positive versus negative compliance
        "ICompReset": 100e-3,
        "SaveData": True
    },

    "Program": {
        "min_gtarget": 100e-6,   # ‑‑ G_Minimum_Target
        "max_gtarget": 1800e-6,  # ‑‑ G_Maximum_Target
        "num_level":   7,        # ‑‑ Num_Levels
        "num":         10,       # ‑‑ Prog_Num
        "num_reads":   10,       # ‑‑ Prog_Num_Reads
        "v_rd":        0.1,      # ‑‑ V_Read
        "v_prg":       1,      # ‑‑ V_Prog_Start
        "v_prg_max":   2.3,      # ‑‑ V_Prog_Max
        "v_count":     0,        # (initial counter)
        "v_countmax":  40,       # ‑‑ V_Count_Max
        "goffset":     10e-6,
        "read_waveform": "Evan_Reram_3",
        "program_waveform": "Evan_Reram_4",
    }


    
}

# Initialize Unified B1500 (includes parameter validation)
b1500 = B1500(unit_label = 'A', parameters=parameters)

# didItShort = b1500.smu.Short_Check(b1500, "Short_Check_Test")
# print(f"We were able to short the two pads?: {didItShort}")

# didItForm = b1500.smu.Forming(b1500, "Form_Test")
# print(f"We Formed the Device?: {didItForm}")

didweSwitch = b1500.smu.Switch_Test(b1500, "Switch_Test")
print(f"Did we successfully switch through all the loops?: {didweSwitch}")
# 
# b1500.smu.connect_smu_list(3)
# b1500.smu.bias_smu(3, 0, 100e-3)

# didweProgram = b1500.wgfmu.ProgramAndRTN(b1500, "Program")
# print(f"Did we successfully Program?: {didweProgram}")

b1500.connection.write("CL")
b1500.wgfmu.wg.WGFMU_clear()




