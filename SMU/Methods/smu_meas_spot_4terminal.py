import numpy as np
def smu_meas_spot_4terminal(self, smu_numD, smu_numG, smu_numS, smu_numB, 
                            VDbias=0.1, VGbias=0, VSbias=0, VBbias=0, 
                            vmeas=0.1, icomp=100e-3, reset_timer=True, disconnect_after=True, clear_settings=True, activate_smus=True):
    """
    Performs a 4-terminal spot measurement.

    Parameters:
    - smu_numD, smu_numG, smu_numS, smu_numB (int): SMU channels for Drain, Gate, Source, Bulk
    - VDbias, VGbias, VSbias, VBbias (float): Bias voltages
    - vmeas (float): Measurement voltage
    - icomp (float): Compliance current
    - reset_timer (bool): Reset timestamp before measurement
    - disconnect_after (bool): Disconnect SMUs after measurement

    Returns:
    - times (numpy array): Time data
    - voltages (numpy array): Voltage data
    - currents (numpy array): Current data
    """
    smu_chD = self.smus[smu_numD - 1]
    smu_chG = self.smus[smu_numG - 1]
    smu_chS = self.smus[smu_numS - 1]
    smu_chB = self.smus[smu_numB - 1]

    # Set measurement format
    self.b1500.write("FMT 1,1")  

    # Configure number of averaging samples
    self.b1500.write("AV 10,1")  

    # Disable SMU filter
    self.b1500.write("FL 1")  

    # Select high-resolution ADC
    self.b1500.write(f"AAD {smu_chD},1")  

    if activate_smus:
        self.b1500.write(f"CN {smu_chD},{smu_chG},{smu_chS},{smu_chB}")  # Connect SMUs

    # Apply bias voltages
    self.b1500.write(f"DV {smu_chD},0,{VDbias},100e-3")  
    self.b1500.write(f"DV {smu_chG},0,{VGbias},100e-3")  
    self.b1500.write(f"DV {smu_chS},0,{VSbias},100e-3")  
    self.b1500.write(f"DV {smu_chB},0,{VBbias},100e-3")  

    # Set compliance mode for the Drain SMU
    self.b1500.write(f"CMM {smu_chD},1")  

    # Enable auto-ranging
    self.b1500.write(f"RI {smu_chD},8")  

    # Reset timestamp before measurement
    if reset_timer:
        self.b1500.write("TSR")  

    # Perform a spot measurement and get timestamp data
    self.b1500.write(f"TTIV {smu_chD},0,0")  
    self.b1500.write("TSQ")  

    # If clear_settings is True, remove biases but keep SMUs active
    if clear_settings:
        self.b1500.write("DZ")  # Zero output to reset the voltage bias
        
    if disconnect_after:
        self.b1500.write(f"CL {smu_chD},{smu_chG},{smu_chS},{smu_chB}")  


    # Read and process data
    # data = self.data_clean(self.b1500.read(), self.parameters)  # Returns a DataFrame
    data = self.b1500.read()
    return data
    
    
    # time_col = f"SMU{smu_numD}_Time"
    # voltage_col = f"SMU{smu_numD}_Voltage"
    # current_col = f"SMU{smu_numD}_Current"

    # try:
    #     time_values = data[time_col].to_numpy(dtype=np.float64)
    #     voltage_values = data[voltage_col].to_numpy(dtype=np.float64)
    #     current_values = data[current_col].to_numpy(dtype=np.float64)

    # except KeyError as e:
    #     missing_col = str(e).strip("'")
    #     print(f"❌ Missing expected column in processed data: {missing_col}\n Returning data array") # REMEMBER THIS DOES NOT STOP THE PROGRAM ITS JUST A PRINT SO YOU CAN SEE WHAT WENT WRONG WITH YOUR DATA
    #     return data  # Return full dataset if missing columns

    # return time_values, voltage_values, current_values
