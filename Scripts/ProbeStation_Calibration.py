# -*- coding: utf-8 -*-
"""
Created on Fri Jul 25 14:06:10 2025

@author: sanand27
"""


from B1500.B1500Unified import B1500
import numpy as np
import matplotlib.pyplot as plt
import time

# Define experiment parameters
parameters = {
    "Name": "Shreenidhi", #These parameters must be changed by the experimenter for better data filing and collection and determines where your data is stored and what it's name is stored as
    "Sample_ID": "GWC331_WGFMU_noise",

    "Waveform Format": "Reram",  # Loads a waveform format (Used in unfinished Waveform creation GUI disregard for now)
    "Waveform": "ReRam_Program_Evan", #Set this to Load a Waveform into the Editor
    # "Waveform Editor": "ask",   #Uncomment this to load the waveform editor on program runtime
    "VDD WGFMU": 2, #This sets what channel of the WGFMU the VDD waveform is applied to
    "VSS WGFMU": 1, #This sets what channel of the WGFMU the VSS waveform is applied to
    "trd": 1e-4, #Used during WGFMU waveform generation
    "pts_per_meas" : 1, #Used during WGFMU waveform generation
    
    
    "wgfmu_readout":{
        "num_read"      : 10,
        "v_rd"          : .1,
        "read_waveform" : "ReRAM_RTN_Evan"
        }
    
}

# Initialize Unified B1500 (includes parameter validation)
b1500 = B1500(unit_label = 'A', parameters=parameters)

didweWGFMU = b1500.wgfmu.wgfmu_readout(b1500, "wgfmu_readout")

b1500.connection.write("CL") #Used to make absolutely sure the B1500 and WGFMU are set to a default safe state upon program exit
b1500.wgfmu.wg.WGFMU_clear()