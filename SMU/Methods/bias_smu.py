def bias_smu( self , smu_num , voltage, Icomp=100e-3 ):
        # Use Keysight SMU numbering. Starts at 1
        smu_ch = self.smus[ smu_num - 1 ]
        #connect = f"CN {smu_ch}"
        bias = f"DV {smu_ch},0,{voltage},{Icomp:.3E}"
        
        #b1500.write( connect )
        self.b1500.write( bias )