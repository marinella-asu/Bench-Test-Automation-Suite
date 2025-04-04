from B1500.B1500Unified import B1500
import numpy as np
import matplotlib.pyplot as plt


# Define experiment parameters
parameters = { #These are all your parameters for your function so they should show up in the method below and at runtime the values you set here will go directly into the program and retention function
    "Name": "Evan",
    "Test Number": "Program-Retention",
    "Die Number": 1,
    "Device Number": 67,
    "Interval": 10e-3,
    "data_points": 300,
    "v_rd": 1,
    "Waveform Format": "Reram",  # Loads "Reram.txt"
    "Waveform": "Evan_Reram_4",  
    "VDD WGFMU": 1,
    "VSS WGFMU": 2,

    #Terminal Setup
    "Drain SMU": 4, 
    "Gate SMU": 1, 
    "Base SMU": 2, 
    "Source SMU": 3,

    # G Parameters
    "G_Minimum": 580e-9, #Bottom Target
    "G_Maximum": 581e-9, #Top Target
    
    "G_MAX": 190e-9,
    "g_offset": 0.1e-9,

    # Voltage & Current Parameters
    "VSTART": 0,
    "VSTOP": 1,
    "ICOMP": 0.1,

    # Sweep & Step Parameters
    "NSTEPS": 101,
    "STEP": 100,
    "SWEEP_TYPE": "DOUBLE",

    # Retention & Programming Parameters
    "V_COUNTMAX": 10,
    "prog_count_max": 1000000,
    "total_retention_time": 60,
    "retention_time": 500e-5,

    # Programming & Reset Parameters
    "vprg": 4,
    "vrst": -10,
    "t_prg": 1.9e-3,
    "v_off": 0
}

    

# Initialize Unified B1500 (includes parameter validation)
b1500 = B1500(unit_label = 'A', parameters=parameters)

b1500.wgfmu.Resalat_Program_and_Retention(b1500, b1500.test_info) #Add the functionality is in method Bench-Test-Automation-Suite-main/WGFMU/Methods/Resalat_Program_and_Retention.py so look there for the actual funcitonality