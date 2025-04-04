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

    #Check For a Short between two SMUS this is a contact measurement
    "Short_Check_Test": { #Must have "_" instead of " "
        "SMU_Pair": [1, 2], #Measure 1 Ground 2
        "Max_Resistance": 200, #200 Ohms or less is a short
        "Max_Voltage": 1, #Max Voltage We can use
        "Dynamic_Check": True, #Do an aautomatic Ramp
        "D_StartV": .1,
        "D_Step": .1, #Step of .5V each time we elapse D_Wait
        "D_Wait": 10
    }

    
}

# Initialize Unified B1500 (includes parameter validation)
b1500 = B1500(unit_label = 'A', parameters=parameters)

didItWork = b1500.smu.Short_Check(b1500, "Short_Check_Test")
print(f"We Found a short?: {didItWork}")




