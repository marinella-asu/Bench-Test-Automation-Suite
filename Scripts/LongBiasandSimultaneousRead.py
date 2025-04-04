from B1500.B1500Unified import B1500
import numpy as np
import matplotlib.pyplot as plt
import time

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
    "smu_numD": 4, 
    "smu_numG": 1, 
    "smu_numB": 2, 
    "smu_numS": 3,
    
    #Programming Bias
    "VDBias": 1,
    "VGBias": 0,
    "VSBias": 0,
    "VBBias": 0,
    
    #Bias Time
    "Wait": 0,
    
    #Read Bias
    "VDBiasRead": 1,
    "VGBiasRead": 0,
    "VSBiasRead": 0,
    "VBBiasRead": 0
}

    

# Initialize Unified B1500 (includes parameter validation)
b1500 = B1500(unit_label = 'A', parameters=parameters)

smu_chD = b1500.smus[b1500.smu_numD - 1]
smu_chG = b1500.smus[b1500.smu_numG - 1]
smu_chS = b1500.smus[b1500.smu_numS - 1]
smu_chB = b1500.smus[b1500.smu_numB - 1]

# Set measurement format
b1500.connection.write("FMT 1,1")  
   
# Configure number of averaging samples
b1500.connection.write("AV 10,1")  
   
# Disable SMU filter
b1500.connection.write("FL 1")  
   
# Select high-resolution ADC
b1500.connection.write(f"AAD {smu_chD},0")
b1500.connection.write(f"AAD {smu_chG},0") 
 
b1500.connection.write(f"CN {smu_chD},{smu_chG},{smu_chS},{smu_chB}")

#Instantiate empty dataframe for storing my in progress data
all_data = np.empty((0, 5))

# Apply bias voltages
b1500.connection.write(f"DV {smu_chD},0,{b1500.VDBias},100e-3")  
b1500.connection.write(f"DV {smu_chG},0,{b1500.VGBias},100e-3")  
b1500.connection.write(f"DV {smu_chS},0,{b1500.VSBias},100e-3")  
b1500.connection.write(f"DV {smu_chB},0,{b1500.VBBias},100e-3")

    
b1500.connection.write("PAD 1")
   
# Set compliance mode for the Drain SMU
b1500.connection.write(f"CMM {smu_chD},1")  
b1500.connection.write(f"CMM {smu_chG},1") 

# Enable auto-ranging
b1500.connection.write(f"RI {smu_chD},8")  
b1500.connection.write(f"RI {smu_chG},8")


b1500.connection.write("TSC 1")
    
b1500.connection.write(f"MM 1, {smu_chD}, {smu_chG}")

# Reset timestamp before measurement
b1500.connection.write("TSR")
results = ""

start_time = time.time()  # Record the start time

while time.time() - start_time < 30:  # Run until 50 seconds have passed
    b1500.connection.write( "XE" ) # Execute measurement
    op_done = b1500.connection.query( "*OPC?" ) # should block until operation completes
    
    
    
    # Read data
    results += b1500.connection.read()
    
    # b1500.connection.write(f"DZ {smu_chD}")  # Zero output to reset the voltage bias
    # b1500.connection.write(f"DZ {smu_chG}")  # Zero output to reset the voltage bias
    
    
    
    # print(f"Waiting for {b1500.Wait} seconds")
    # time.sleep(b1500.Wait)  # Pauses execution for a variable number of seconds
    # print("Done waiting!")

data = b1500.data_clean(b1500, results, b1500.test_info.parameters, NoSave = False)
# current_drain = data.get("SMU4_Current", None)
# time_drain = data.get("SMU4_Time", None)
# current_Gate = data.get("SMU1_Current", None)
# time_gate = data.get("SMU1_Time", None)


# #Now we take the data and put it into useful variables and set our current conductance
# current_program = float(current_drain[0])
# time_program = float(time_drain[0])

# time_Gate_program = float(time_gate[0])
# current_Gate_program = float(current_Gate[0])

# g_cur = current_program/(b1500.VDBias)

# # Float values to append
# new_data = [time_Gate_program, current_Gate_program, time_program, current_program, g_cur] #Conductance, Drain V, Gate V

# # Append the new data (a pair of floats) to the all_data array
# all_data = np.append(all_data, [new_data], axis=0)

b1500.connection.write("CL")
# b1500.save_numpy_to_csv(b1500.test_info, all_data, filename = "Simultaneous Spot Measurement")