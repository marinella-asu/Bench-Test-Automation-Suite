import numpy as np
import matplotlib.pyplot as plt
import datetime

def prg_2terminal(self, b1500=None, param_name=None, v_prg = 1, v_prg_max = 9.8, v_rd = .1, vstep = 0.1, gmin = 300e-6, gmax = 1000e-6, pulses_per_voltage = 30, **overrides):

    now = datetime.datetime.now()
    date_time = now.strftime("%Y-%m-%d_%H-%M-%S")

    final_params = {
        "v_prg": v_prg,
        "v_prg_max": v_prg_max,
        "v_rd": v_rd,
        "vstep": vstep,
        "gmin": gmin,
        "gmax": gmax,
        "pulses_per_voltage": pulses_per_voltage
    }

    if b1500 and param_name:
        param_block = dict(b1500.parameters.get(param_name, {}))
        param_block.update(overrides)
        for key, value in param_block.items():
            setattr(b1500, f"{key}_{param_name}", value)
        final_params.update(param_block)

    if not b1500 or not param_name:
        final_params.update(overrides)

    v_prg = final_params["v_prg"]
    v_prg_max = final_params["v_prg_max"]
    v_rd = final_params["v_rd"]
    vstep = final_params["vstep"]
    gmin = final_params["gmin"]
    gmax =  final_params["gmax"]
    pulses_per_voltage = final_params["pulses_per_voltage"]


    v_prg_set = v_prg
    v_prg_rst = -v_prg

    pulse_num = 0
    
    done = False #Done flag
    
    results = self.rd_pulses_Resalat(b1500, alternate_waveform = "Evan_Reram_4")
    #print(f'{results[2]}')
    g_cur = sum(results[2])/len(results[2])
    #print(f"conductance {sum(results[2])/len(results[2])} and {g_cur}")
    #g_cur = st.mean([results[1][2], results[2][2], results[3][2], results[4][2]])
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
            v_prg_set = v_prg_set + vstep_increment
            v_prg = v_prg_set
            operation = "SET"
        elif rst_done==False:
            v_prg_rst = v_prg_rst - vstep_increment
            v_prg = v_prg_rst
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
            
        
        pulse_num += 1
        if (pulse_num<pulses_per_voltage):
            vstep_increment = 0
        else:
            vstep_increment = vstep
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