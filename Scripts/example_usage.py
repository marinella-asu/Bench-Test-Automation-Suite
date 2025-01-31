from B1500.B1500Unified import B1500

# Define experiment parameters
parameters = {
    "Name": "Evan",
    "Test Number": "ask",
    "Die Number": 1,
    "Device Number": 67,
    "Read Voltage": 100,
    "Compliance Current": 100,
    "Pulse Voltage": 100,
    "Pulse Duration": 101,
}

# Initialize Unified B1500 (includes parameter validation)
b1500 = B1500(parameters=parameters)

# b1500.wgfmu.check_errors()
b1500.smu.IVSweep(smu_num = 3)
