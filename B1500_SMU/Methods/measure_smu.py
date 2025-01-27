import numpy as np
### Matthew Measure command
def measure_smu( self , smu_num, vmeas, icomp=100e-3 ):
    # Use Keysight SMU numbering. Starts at 1
    smu_ch = self.smus[ smu_num - 1 ]
    #connect = f"CN {smu_ch}"
    # Initial B1500 Measurement Setup
    smu_ind = smu_num - 1
    smu_ch = self.smus[ smu_ind ] 
    self.b1500.write( "FMT 1,1")
    self.b1500.write( "AV 10,1" ) # Set number of averaging samples
    self.b1500.write( "FL 1" ) # Disable SMU Filter. Not sure if should be enabled or disabled
    self.b1500.write( f"AAD {smu_ch},1" ) # 0: fast ADC, 1: HR ADC
    
    # Enable timestamps
    self.b1500.write( "TSC 1" )
    
    # Bias VMEAS
    self.b1500.write( f"CN {smu_ch}" )
    
    # Set up sampling measurement
    self.b1500.write( f"MV {smu_ch},0,0,{vmeas},{icomp}") # Bias settings
    self.b1500.write( f"MM 10,{smu_ch}" ) # Measurement mode: sampling measurement on smu_ch
    self.b1500.write( f"CMM {smu_ch},0" ) # 0: compliance side measurement, 1: current measurement
    
    data = self.b1500.read()
    
    return data