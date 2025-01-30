def multichan_pulsed_spot(self, smu_numD, smu_numG, smu_numS, smu_numB, vmeasDSB, vmeasG, icompDSB, icompG,  interval, pre_bias_time, number, disconnect_after=True, plot_results=False ):
        
        # Initial B1500 Measurement Setup
        smu_indD = smu_numD - 1
        smu_chD = self.smus[ smu_indD ] 
        smu_indG = smu_numG - 1
        smu_chG = self.smus[ smu_indG ] 
        smu_indS = smu_numS - 1
        smu_chS = self.smus[ smu_indS ] 
        smu_indB = smu_numB - 1
        smu_chB = self.smus[ smu_indB ] 
    
        #orig below
        #self.b1500.write( "FMT 1,1")
        self.b1500.write("FMT 3,1")
        self.b1500.write( "FL 0" ) # Disable SMU Filter. Not sure if should be enabled or disabled
        self.b1500.write( "TSC 1" )
        
        self.b1500.write( f"CN {smu_chD}" )
        self.b1500.write( f"CN {smu_chG}" )
        self.b1500.write( f"CN {smu_chS}" )
        self.b1500.write( f"CN {smu_chB}" )
        
        
        #0.000001 can be set to interval and adjusted 
        self.b1500.write("AIT 2,3,0.000001")
    
        #command syntax MCPT hold,period,mdelay,average
        self.b1500.write("MCPT 0,0.00005,0,1")
    
        #command syntax MCPNT chnum,delay,width used for MM27 or MM28
        self.b1500.write("MCPNT {smu_chD},0,0.00005")
        #command syntax MCPNX N,chnum,mode,range,base,pulse,comp #example uses 3 for pulse
        self.b1500.write("MCPNX 1,{smu_chD},1,0,0,5,{icompDSB}")
        self.b1500.write("MCPNT {smu_chG},0,0.00005")
        self.b1500.write("MCPNX 2,{smu_chG},1,0,0,5,{icompG}")
        self.b1500.write("MCPNT {smu_chS},0,0.00005")
        self.b1500.write("MCPNX 3,{smu_chS},1,0,0,5,{icompDSB}")
        self.b1500.write("MCPNT {smu_chB},0,0.00005")
        self.b1500.write("MCPNX 4,{smu_chB},1,0,0,5,{icompDSB}")
        
        #applying direct votlages 
        self.b1500.write( f"DV {smu_chD},0,{vmeasDSB},{icompDSB}" )
        self.b1500.write( f"DV {smu_chG},0,{vmeasG},{icompG}" )
        self.b1500.write( f"DV {smu_chS},0,{vmeasDSB},{icompDSB}" )
        self.b1500.write( f"DV {smu_chB},0,{vmeasDSB},{icompDSB}" )
        

        #command syntax MM mode, chnum, chnum, chnum
        self.b1500.write( f"MM 27,{smu_chD},{smu_chG},{smu_chS},{smu_chB}" ) # Measurement mode: sampling measurement on smu_ch
        #self.b1500.write( f"MM 27,{smu_chG}" ) # Measurement mode: sampling measurement on smu_ch
        #self.b1500.write( f"MM 27,{smu_chS}" ) # Measurement mode: sampling measurement on smu_ch
        #self.b1500.write( f"MM 27,{smu_chB}" ) # Measurement mode: sampling measurement on smu_ch
        
        #setting compliance
        self.b1500.write( f"CMM {smu_chD},0" ) # 0: compliance side measurement, 1: current measurement
        self.b1500.write( f"CMM {smu_chG},0" ) # 0: compliance side measurement, 1: current measurement
        self.b1500.write( f"CMM {smu_chS},0" ) # 0: compliance side measurement, 1: current measurement
        self.b1500.write( f"CMM {smu_chB},0" ) # 0: compliance side measurement, 1: current measurement
        
        #setts current range 
        self.b1500.write(f"RI {smu_chD},0")
        self.b1500.write(f"RI {smu_chG},0")
        self.b1500.write(f"RI {smu_chB},0")
        self.b1500.write(f"RI {smu_chS},0")
        
        
        # Reset timestamp and perform measurement
        self.b1500.write( "TSR" ) # Resets timestamp for all SMU channels
        self.b1500.write( "XE" ) # Execute measurement
        op_done = self.b1500.query( "*OPC?" ) # should block until operation completes
        
        
        if disconnect_after:
            self.b1500.write( f"CL {smu_chD},{smu_chG},{smu_chS},{smu_chB}" )