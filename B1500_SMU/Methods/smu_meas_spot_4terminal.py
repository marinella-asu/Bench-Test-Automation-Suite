def smu_meas_spot_4termininal( self, smu_numD, smu_numG, smu_numS, smu_numB,VDbias = 0.1, VGbias = 0,VSbias = 0, VBbias = 0 , vmeas=0.1 , icomp=100e-3 , reset_timer=True , disconnect_after=True ):
            # Performs a spot measurement and then disconnects and zeros all SMUs
            
            smu_idxD = smu_numD - 1
            smu_idxG = smu_numG - 1
            smu_idxS = smu_numS - 1
            smu_idxB = smu_numB - 1
            smu_chD = self.smus[ smu_idxD ] 
            smu_chG = self.smus[ smu_idxG ]
            smu_chS = self.smus[ smu_idxS ]
            smu_chB = self.smus[ smu_idxB ]
            self.b1500.write( "FMT 1,1")
            self.b1500.write( "AV 10,1" ) # Set number of averaging samples
            self.b1500.write( "FL 1" ) # Disable SMU Filter. Not sure if should be enabled or disabled
            self.b1500.write( f"AAD {smu_chD},1" ) # 0: fast ADC, 1: HR ADC
            
            # Connect SMUS
            self.b1500.write( f"CN {smu_chD},{smu_chG},{smu_chS},{smu_chB}" )
            
            #Syntax DV chnum,vrange,voltage[,Icomp[,comp_polarity[,irange]]
            # Set Biases
            self.b1500.write( f"DV {smu_chD},0,{VDbias},100e-3" )
            self.b1500.write( f"DV {smu_chG},0,{VGbias},100e-3" )
            self.b1500.write( f"DV {smu_chS},0,{VSbias},100e-3" )
            self.b1500.write( f"DV {smu_chB},0,{VBbias},100e-3" )
            
            self.b1500.write( f"CMM {smu_chD},1" )
            self.b1500.write( f"RI {smu_chD},8" )
            
            # Reset timestamp and perform measurement
            if reset_timer:
                self.b1500.write( "TSR" ) # Resets timestamp for all SMU channels
            self.b1500.write( f"TTIV {smu_chD},0,0" ) # Performs high speed spot measurement and returns data and time 
            self.b1500.write( "TSQ" ) # returns time data from when the TSR command is sent until now
            
            self.b1500.write( f"DZ {smu_chD}" )
            if disconnect_after:
                self.b1500.write( f"CL {smu_chD},{smu_chG},{smu_chS},{smu_chB}" )
            
            data = self.b1500.read()
            
            times , voltages , currents = self.process_data_str_tiv( data )
            
            return ( times , voltages , currents )