import numpy as np
import matplotlib.pyplot as plt

def prg_2terminal(self, b1500, DEBUG_PRINT = False):
    v_prg_max=9.9 #Default for Voltage Program Max: If you want to change this set a Program Max Voltage parameter
    if hasattr(b1500.test_info, "Program_Max_Voltage"):
        v_prg_max = b1500.test_info.Program_Max_Voltage
    
    gmin=0e-6 #Default for GMinimum: Set a G_Minimum parameter if you want this to be different
    if hasattr(b1500.test_info, "G_Minimum"):
        gmin = b1500.test_info.G_Minimum
    
    gmax=0e-6 #Default for GMaximum: Set a G_Maximum parameter if you want this to be different
    if hasattr(b1500.test_info, "G_Maximum"):
        gmax = b1500.test_info.G_Maximum

    pulses_per_voltage=10 #Default for Pulse_Per_V
    if hasattr(b1500.test_info, "Pulse_Per_V"):
        pulses_per_voltage = b1500.test_info.Pulse_Per_V

    num_pgms=1 #Defualt for Number_of_Programs
    if hasattr(b1500.test_info, "Number_of_Programs"):
        num_pgms = b1500.test_info.Number_of_Programs

    vstep_param = .1 #Default Step Parameter
    if hasattr(b1500.test_info, "V_Step"):
        vstep_param = b1500.test_info.V_Step

    _, v_prg_set = b1500.test_info.VSS_Set #assume when I program or reset its using VSS and VDD is for read
    _, v_prg_rst = b1500.test_info.VSS_Reset
    v_prg = 0

    done = False #Done flag

    results = self.rd_pulses_Resalat(b1500.test_info, alternate_waveform = "Evan_Reram_3")
    #print(f'{results[2]}')
    g_cur = sum(results[2])/len(results[2])
    #print(f"conductance {sum(results[2])/len(results[2])} and {g_cur}")
    #g_cur = st.mean([results[1][2], results[2][2], results[3][2], results[4][2]])
    if DEBUG_PRINT:
        print( f"..Init Level Read: {g_cur*1e9:.4g} nS [{gmin*1e9:.4g} nS, {gmax*1e9:.4g} nS] ")
    ##############################################
    
    if (g_cur >= gmin) and (g_cur <= gmax):
        done = True
    
        
    while done==False and v_prg < v_prg_max:
        # try:
        #     g_cur = float(g_cur)
        # except ValueError:
        #     print("Variable g_cur is not a numberical type")
            
        set_done = ( g_cur >= gmin )
        rst_done = ( g_cur <= gmax )
        done = np.all(set_done & rst_done)
        
        print(f"value of conductance {g_cur:.4g}, SET {set_done}, RESET {rst_done}, and DONE {done}")
        if set_done==False:
            v_prg_set = v_prg_set + vstep
            v_prg = v_prg_set
            b1500.test_info.update_set(b1500.test_info, set_voltage = v_prg_set)
            operation = "SET"
        elif rst_done==False:
            v_prg_rst = v_prg_rst - vstep
            v_prg = v_prg_rst
            b1500.test_info.update_set(b1500.test_info, reset_voltage = v_prg_rst)
            operation = "RESET"
        
        
        # clear existing pattern data
        self.wg.WGFMU_clear()
        
        # Create waveform on WGFMU
        self.create_waveform(b1500.test_info)
        
        self.wgfmu_run([b1500.test_info.ch_vdd , b1500.test_info.ch_vss ])
        
        ###################### SHALL IT BETTER TO USE A SEPERATE READ FUNCTION INSTEAD OF COMBINED READ WITHIN THE PROGRAM ONE?
        # Read out data
        times1, vals1 = self.read_results( b1500.test_info.ch_vdd )
        times2, vals2 = self.read_results( b1500.test_info.ch_vss )
        
        # Close down WGFMU Session
        times = times1
        currents = vals1
        # print(f"currents {vals1}")
        conductances = currents / b1500.test_info.VDD_rd
        g_cur = conductances[-1]
        current = currents[-1]
        #print(f"end of a loop: {g_cur}")
        if DEBUG_PRINT:
            print( f"{operation}   {v_prg:.4g} V \t {g_cur*1e9:.4g} nS \t [{gmin*1e9:.4g} nS,{gmax*1e9:.4g}] nS {done} \t  ({current*1e6:.3g} uA)" )
            
        
        pulse_num += 1
        if (pulse_num<pulses_per_voltage):
            vstep = 0
        else:
            vstep = vstep_param
            pulse_num = 0
        # level_num = np.floor( pulse_num / pulses_per_voltage )
        # vstep = level_num*vstep
        
        # pulse_num += 1
        # level_num = np.floor( pulse_num / pulses_per_voltage )
        # v_pgm = v_start + v_inc*level_num
    
        # if offset_times:
        #     t_offset = t_run
        #     times += t_offset
        # else:
        #     t_offset = 0
    
        if ((abs(v_prg)>v_prg_max)):
            print("The device is unprogrammable - Bias Condition Is Over {v_prg_max} V")
        elif (done):
            #print( f"The program operation succeeds with conductance of {g_cur*1e6:.4g} uS \t at bias condition {v_prg:.4g} V \t ({currents*1e6:.3g} uA)")
            print( f"The program operation succeeds with conductance of {g_cur*1e9:.4g} nS \t at bias condition {v_prg:.4g} V \t  ({current*1e6:.3g} uA)")
        
    return ( times , currents , g_cur, conductances )