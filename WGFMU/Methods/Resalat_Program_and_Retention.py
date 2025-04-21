##3 Bottom gate, 5/2 source, 4 drain, 1 top

##********************IMPORTANT********************##
#Before running, check:
    #1. SMUs
    #2. output_dir path
    #3. v_prg
    #4. t_prg
    #5. g_min and g_max values.
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import csv
import os
import sys
import re
import ctypes as ct # Convert between python and C data types (needed for WGFMU)
import numpy as np

#Channel 1 is VSS
#Channel 2 is VDD
#target conductance
def Resalat_Program_and_Retention(self, b1500):
    min_gtarget = b1500.test_info.parameters.get("G_Minimum", 40e-9)
    max_gtarget = b1500.test_info.parameters.get("G_Maximum", 130e-9)
    G_MAX = b1500.test_info.parameters.get("G_MAX", 190e-9)
    STEP = b1500.test_info.parameters.get("STEP", 1)
    g_offset = b1500.test_info.parameters.get("g_offset", 0.1e-9)
    V_COUNTMAX = b1500.test_info.parameters.get("V_COUNTMAX", 10)
    prog_count_max = b1500.test_info.parameters.get("prog_count_max", 10)
    total_retention_time = b1500.test_info.parameters.get("total_retention_time", 60)
    retention_time = b1500.test_info.parameters.get("retention_time", 500e-5)
    data_points = b1500.test_info.parameters.get("data_points", 30000)
    smu_num = b1500.test_info.parameters.get("smu_num", 4)
    VSTART = b1500.test_info.parameters.get("VSTART", 0)
    VSTOP = b1500.test_info.parameters.get("VSTOP", 1)
    ICOMP = b1500.test_info.parameters.get("ICOMP", 0.1)
    NSTEPS = b1500.test_info.parameters.get("NSTEPS", 101)
    SWEEP_TYPE = b1500.test_info.parameters.get("SWEEP_TYPE", "DOUBLE")
    v_rd = b1500.test_info.parameters.get("Voltage_Read", 1)
    vprg = b1500.test_info.parameters.get("vprg", 4)
    vrst = b1500.test_info.parameters.get("vrst", -6)
    t_prg = b1500.test_info.parameters.get("t_prg", 1.9e-3)
    v_off = b1500.test_info.parameters.get("v_off", 0)



    #Setup Variables and Flags
    now = datetime.datetime.now()
    date_time = now.strftime("%Y-%m-%d_%H-%M-%S")  
    done=True
    gtargets = np.linspace(min_gtarget, max_gtarget, num=STEP)
    gtargets = np.linspace(min_gtarget, max_gtarget, num=STEP)
    succeed_prg = False
    verification_requirement = True #Turn this one TRUE if you want to verify after program
    if SWEEP_TYPE == "DOUBLE":
        mode=3
    else:
        mode=1

    #Initial Sweep
    # b1500.smu.IVSweep(smu_num, vstart=VSTART , vstop=VSTOP , nsteps=NSTEPS , mode=mode, icomp=ICOMP, connect_first=True, disconnect_after=True , plot_data=True)

    # result_read = b1500.smu_meas_sweep( 4 , vstart=0 , vstop=1 , nsteps=101 , mode=1, icomp=100e-3, num_averaging_samples=1 , connect_first=True, disconnect_after=True , plot_data=True)
    # times = result_read[0]
    # currents = result_read[2]
    # init_cond = currents[-1]/1
    # print( f"Conductance for 1V:    {(init_cond)*1e9:.4g} nS" )

    read_initial = b1500.smu.smu_meas_spot_4terminal(smu_numD=4, smu_numG=1, smu_numS=3, smu_numB=2, VDbias = v_rd, VGbias = 0,VSbias = 0, VBbias = 0 , vmeas=0.1 , icomp=100e-3 , reset_timer=True , disconnect_after=True )
    #This steps takes the raw B1500 data and turns it into clean collumns we can use
    data = b1500.data_clean(b1500, read_initial, b1500.test_info.parameters, NoSave = True)
    time_drain = data.get("SMU4_Time", None)
    current_drain = data.get("SMU4_Current", None)

    #Now we take the data and put it into useful variables and set our initial conductance
    current_initial = float(current_drain[0])
    time_initial = float(time_drain[0])
    cond_initial = current_initial
    g_d = cond_initial
    print(f"\nTHE INITIAL CONDUCTANCE IS: {g_d*1e9}nS")
    
    # # IV sweep
    # result_iv = b1500.smu.IVSweep(
    #     smu_nums = 4,
    #     vstart=0,
    #     vstop=1,
    #     nsteps=101,
    #     mode=1,
    #     icomp=100e-3,
    #     num_averaging_samples=1,
    #     connect_first=True,
    #     disconnect_after=True,
    #     plot_data=False,
    #     vmax_override=True
    # )

    # times_iv = result_iv[0]
    # voltage_iv = result_iv[1]
    # currents_iv = result_iv[2]
    
    # plt.figure()
    # plt.plot(voltage_iv, currents_iv)
    # plt.xlabel("Voltage (V)")
    # plt.ylabel("Current (A)")
    # plt.show()
    
    # print(f'Finished IV sweep for {gtarget*1e9:.4g} nS.')u_numG=1, smu_numS=3, smu_numB=4,VDbias = v_rd, VGbias = 0,VSbias = 0, VBbias = 0 , vmeas=0.1 , icomp=100e-3 , reset_timer=True , disconnect_after=True )


    # if g_d*1e9 > max_gtarget*1e9:
    #     print("reset device first")
    #     sys.exit()
    #     # plot the results
    #     plt.figure()
    #     plt.plot(time_initial, cond_initial*1e9)
    #     plt.title("Starting Conductance vs Time" )
    #     plt.xlabel("Time (s)")
    #     plt.xlabel("Conductance (nS)")
    #     plt.show()
    #     plt.close()    

    
    # results = b1500.connection.read()
    # b1500.data_clean(b1500, results, b1500.parameters)

    # Initialize a list to store the pulse information
    pulse_data = []
    
    #Instantiate empty dataframe for storing my in progress data
    all_data = np.empty((0, 7))
    
    
    
    ##LOOP THROUGH GTARGETS##
    try:
        for i, gtarget in enumerate(gtargets):
            print(f"\n\nTHE TARGET CONDUCTANCE IS:{gtarget*1e9}nS\n\n\n")
            v_prg = vprg
            v_rst = vrst
            v_count = 0
            g_min = gtarget - 0.25e-9
            g_max = gtarget + 0.75e-9
            print(g_min*1e9)
            print(g_max*1e9)
            print(g_d*1e9)

            while not succeed_prg:
                if (g_d<g_min) or (g_d>g_max):
                    done=False
                    print("\nProgramming or Erasing device")
                    print(f"\nThe state of program condition [{done}]\n\n")    
                #Program with (V_PRG)V pulse at (t_prg)sec width
                # results = qn.prg_2terminal( ch_vdd=ch_vdd, ch_vss = ch_vss, v_prg = v_prg, v_prg_max=9.9,
                #                             v_rd=v_rd , t_prg=t_prg, ranging_rd=wgc.WGFMU_MEASURE_CURRENT_RANGE_1UA, gmin=g_min , gmax=g_max , pulses_per_voltage=15)
                pulse_num=0
                g_cur=g_d
                vstep = 0
            
                while done == False:
                    print("\nIn the Prgramming or erasing loop.\n")
                    set_done = ( g_cur >= g_min )
                    rst_done = ( g_cur <= g_max )
                    done = np.all(set_done & rst_done)
                    
                    
                    if abs(v_prg)>19 or abs(v_rst)>16:
                        print("Max Program Voltage Reached. Stopping...")
                        sys.exit()
                    if g_cur >= g_max:
                        print("\nIn the Erasing loop.\n")
                        v_rst = v_rst - vstep
                        results = b1500.smu.smu_meas_sample_multi_term( smu_numD = 4, 
                                                                smu_numG = 1, 
                                                                smu_numS = 3, 
                                                                smu_numB = 2, 
                                                                vmeasD=0,
                                                                vmeasG=v_rst,
                                                                vmeasS=0, 
                                                                vmeasB=0,
                                                                icompDSB=100e-3, 
                                                                icompG=0.1,  
                                                                interval=t_prg, 
                                                                pre_bias_time=0, 
                                                                number=2, 
                                                                disconnect_after=False, 
                                                                plot_results=False )
                        
                        print(f'Measurement results of Program: {results}')
                        data = b1500.data_clean(b1500, results, b1500.test_info.parameters, NoSave = True)
                        time_drain = data.get("SMU4_Time", None)
                        current_drain = data.get("SMU4_Current", None)
                        
                        time_Gate = data.get("SMU1_Time", None)
                        current_Gate = data.get("SMU1_Current", None)
                        
                        #Now we take the data and put it into useful variables and set our current conductance
                        current_program = float(current_drain[0])
                        time_program = float(time_drain[0])
                      
                        current_Gate_program = float(current_Gate[0])
                        time_Gate_program = float(time_Gate[0])
                        
                        
                        read_verify = b1500.smu.smu_meas_spot_4terminal(smu_numD=4, smu_numG=1, smu_numS=3, smu_numB=2,VDbias = v_rd, VGbias = 0,VSbias = 0, VBbias = 0 , vmeas=0.1 , icomp=100e-3 , reset_timer=True , disconnect_after=True )
                        print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n')
                        print(f'Spot meas Current: {current_initial}')
                        #This steps takes the raw B1500 data and turns it into clean collumns we can use
                        data = b1500.data_clean(b1500, read_verify, b1500.test_info.parameters, NoSave = True)
                        time_drain = data.get("SMU4_Time", None)
                        current_drain = data.get("SMU4_Current", None)
                        
                        # time_Gate = data.get("SMU1_Time", None)
                        # current_Gate = data.get("SMU1_Current", None)
                        
                        #Now we take the data and put it into useful variables and set our current conductance
                        current_initial = float(current_drain[0])
                        time_initial = float(time_drain[0])
                      
                        # current_Gate_initial = float(current_Gate[0])
                        # time_Gate_initial = float(time_Gate[0])
                        
                        # if (time_Gate_initial == time_initial):
                        #     print("\n\n\n\n\n\n*********\n\n\n\n\n")
                        cond_initial = current_initial
                        g_cur = cond_initial
                        print(f"\nThe state of the program is at {g_cur*1e9}nS, Target is [{g_min*1e9}nS, {g_max*1e9}nS], with applied voltage of {v_rst}V with condition [{done}]\n\n")
                        
                        # Float values to append
                        new_data = [pulse_num, time_Gate_program, current_Gate_program, time_program, current_program, g_cur, v_rst] #Conductance, Drain V, Gate V

                        # Append the new data (a pair of floats) to the all_data array
                        all_data = np.append(all_data, [new_data], axis=0)
                        
                        pulse_num += 1
                        pulse_data.append([v_rst, g_cur[0] if isinstance(g_cur, (list, np.ndarray)) else g_cur])  # Store conductance as scalar
                    
                        if (pulse_num<prog_count_max):
                            vstep = 0
                        else:
                            vstep = 0.1
                            pulse_num = 0
                    if g_cur <= g_min:
                        print("\nIn the Prgramming loop.\n")
                        v_prg = v_prg + vstep
                        results = b1500.smu.smu_meas_sample_multi_term( smu_numD = 2, 
                                                                smu_numG = 1, 
                                                                smu_numS = 3, 
                                                                smu_numB = 4, 
                                                                vmeasD=0,
                                                                vmeasG=v_prg,
                                                                vmeasS=0, 
                                                                vmeasB=0,
                                                                icompDSB=100e-3, 
                                                                icompG=0.1,  
                                                                interval=t_prg, 
                                                                pre_bias_time=0, 
                                                                number=2, 
                                                                disconnect_after=False, 
                                                                plot_results=False )
                
                        print(f'Measurement results of Program: {results}')
                        read_verify = b1500.smu.smu_meas_spot_4terminal(smu_numD=4, smu_numG=1, smu_numS=3, smu_numB=2,VDbias = v_rd, VGbias = 0,VSbias = 0, VBbias = 0 , vmeas=0.1 , icomp=100e-3 , reset_timer=True , disconnect_after=True )
                        print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n')
                        print(f'Spot meas Current: {current_initial}')
                        #This steps takes the raw B1500 data and turns it into clean collumns we can use
                        data = b1500.data_clean(b1500, read_verify, b1500.test_info.parameters, NoSave = True)
                        time_drain = data.get("SMU4_Time", None)
                        current_drain = data.get("SMU4_Current", None)

                        #Now we take the data and put it into useful variables and set our current conductance
                        current_initial = float(current_drain[0])
                        time_initial = float(time_drain[0])
                        cond_initial = current_initial
                        g_cur = cond_initial
                        print(f"\nThe state of the program is at {g_cur*1e9}nS, Target is [{g_min*1e9}nS, {g_max*1e9}nS], with applied voltage of {v_prg}V with condition [{done}]\n\n")
                        pulse_num += 1
                        pulse_data.append([v_prg, g_cur[0] if isinstance(g_cur, (list, np.ndarray)) else g_cur])  # Store conductance as scalar
                        

                        if (pulse_num<prog_count_max):
                            vstep = 0
                        else:
                            vstep = 0.1
                            pulse_num = 0

            
                if verification_requirement == True:
                    read_verification = b1500.smu.smu_meas_spot_4terminal(smu_numD=4, smu_numG=1, smu_numS=3, smu_numB=2,VDbias = v_rd, VGbias = 0,VSbias = 0, VBbias = 0 , vmeas=0.1 , icomp=100e-3 , reset_timer=True , disconnect_after=True )
                    #This steps takes the raw B1500 data and turns it into clean collumns we can use
                    data = b1500.data_clean(b1500, read_verify, b1500.test_info.parameters, NoSave = True)
                    time_drain = data.get("SMU4_Time", None)
                    current_drain = data.get("SMU4_Current", None)
                    
                    conduction_verification = float(current_drain[0]) #get our current for verification
                    g_min1 = g_min - g_offset
                    g_max1 = g_max + g_offset
                    if (conduction_verification>g_min1) or (conduction_verification<g_max1):
                        done = True
                    else:
                        done = False
                        
                    
                # # Quick read to check conductance after program
                # read_test = self.rd_pulses_Resalat_noise(b1500.test_info, alternate_waveform= "Evan_Reram_3")
                # # ^ This was the original parameters I used, the other version below has a larger t_settle. Have to test the effects of this. #

                # read_test = self.rd_pulses_Resalat_noise(b1500.test_info, alternate_waveform= "Evan_Reram_3")


                # cond_test = read_test[2]
                # current_test = read_test[1]
                # time_test = read_test[0]
                # all_except_first = cond_test[1:]
                # g_d = sum(all_except_first)/len(all_except_first)
                # print(f"Quick Read Avg Conductance: {g_d*1e9}")        

                # gmin1 = gtarget - 2e-9 #offsetting since WGFMU measured conductance is about 3e-9 higher than accurate readings from SMU
                # gmax1 = gtarget
                # succeed_prg = (g_d >= gmin1) and (g_d <= gmax1)  #check that target is reached.
                
                succeed_prg = True
                #v_prg=v_prg_initial
                #v_rst=v_rst_initial
                ##important checks to make sure device doesn't break##
                # Check that conductance is lower than 150nS
                # if g_d >= G_MAX:
                #     print("******Device Max Conductance reached, stopping program at risk of damaging device******")
                #     sys.exit()
                #Stop after reaching max number of program 
                if v_count >= V_COUNTMAX - 1:
                    print(f"******Did not reach target conductance {gtarget*1e9}nS, stopping program because V_COUNTMAX reached******")
                    sys.exit()
                v_count += 1
                
                # if not succeed_prg:
                #     print(f"******Not within requirements {gmin1*1e9}nS and {gmax1*1e9}nS. Try increasing t_prg in program function if possible.******")
                
                #if target reached, start long term read
                    
                #program results
                time_prg = time_initial
                curr_prg = current_initial
                cond_prg = g_cur

                data_prg_list = [time_prg, curr_prg, cond_prg]
                data_prg_array = np.array(data_prg_list)
                
                b1500.save_numpy_to_csv(b1500.test_info, data_prg_array, filename="Program_Data")

                print("\nTarget Conductance Reached. Holding the gate voltage at -0.1 for 60s\n")
                
                # results = b1500.smu.smu_meas_sample_multi_term( smu_numD = 2, 
                #                                         smu_numG = 1, 
                #                                         smu_numS = 3, 
                #                                         smu_numB = 4, 
                #                                         vmeasD=0,
                #                                         vmeasG=-0.1,
                #                                         vmeasS=0, 
                #                                         vmeasB=0,
                #                                         icompDSB=100e-3, 
                #                                         icompG=0.1,  
                #                                         interval=60, 
                #                                         pre_bias_time=0, 
                #                                         number=2, 
                #                                         disconnect_after=False, 
                #                                         plot_results=False )
                print("\Starting the 5 min Read\n")
                smu_numD = 1  
                smu_numG = 4 
                smu_numS = 3 
                smu_numB = 2
                
                results_read = b1500.smu.smu_meas_sample_multi_term_int( smu_numD = smu_numD, 
                                                    smu_numG = smu_numG, 
                                                    smu_numS = smu_numS, 
                                                    smu_numB = smu_numB, 
                                                    vmeasD=0,
                                                    vmeasG=v_rd,
                                                    vmeasS=0, 
                                                    vmeasB=0,
                                                    icompDSB=1e-6, 
                                                    icompG=1e-6,  
                                                    interval=10e-3,
                                                    pre_bias_time=0, 
                                                    number=data_points, 
                                                    disconnect_after=False, 
                                                    plot_results=False, 
                                                    int_num=50)
                
                data = b1500.data_clean(b1500, results_read, b1500.test_info.parameters, NoSave = False)
                extracted_data = []
                time_col = f"SMU{smu_numG}_Time (s)"
                voltage_col = f"SMU{smu_numG}_Voltage (V)"
                current_col = f"SMU{smu_numG}_Current (A)"
                
                Drain_time_col = f"SMU{smu_numD}_Time (s)"
                Drain_voltage_col = f"SMU{smu_numD}_Voltage (V)"
                Drain_current_col = f"SMU{smu_numD}_Current (A)"

                try:
                    time_values = data[time_col].to_numpy(dtype=np.float64)
                    voltage_values = data[voltage_col].to_numpy(dtype=np.float64)
                    current_values = data[current_col].to_numpy(dtype=np.float64)
                    
                    Drain_time_values = data[Drain_time_col].to_numpy(dtype=np.float64)
                    Drain_voltage_values = data[Drain_voltage_col].to_numpy(dtype=np.float64)
                    Drain_current_values = data[Drain_current_col].to_numpy(dtype=np.float64)

                except KeyError as e:
                    missing_col = str(e).strip("'")
                    print(f"❌ Missing expected column in processed data: {missing_col}\n Returning data array") # REMEMBER THIS DOES NOT STOP THE PROGRAM ITS JUST A PRINT SO YOU CAN SEE WHAT WENT WRONG WITH YOUR DATA
                    return data  # Return full dataset if missing columns
        

                pulse_count = time_values #HEY FIX THIS WAt!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                current_read = voltage_values
                time_read = current_values

                cond_read = current_read/v_rd
                # print(results_read)
                
                # results = b1500.smu.smu_meas_sweep( 2 , vstart=0 , vstop=1 , nsteps=101 , mode=3, icomp=1e-1, num_averaging_samples=1 , connect_first=True, disconnect_after=True , plot_data=True, vmax_override=True )

                # # g_d = sum(cond_read)/len(cond_read)
                # # print(f"300sec Read Avg Conductance: {g_d*1e9}")


                # # IV sweep
                # result_iv = b1500.smu.IVSweep(
                #     smu_nums = 4,
                #     vstart=0,
                #     vstop=1,
                #     nsteps=101,
                #     mode=1,
                #     icomp=100e-3,
                #     num_averaging_samples=1,
                #     connect_first=True,
                #     disconnect_after=True,
                #     plot_data=False,
                #     vmax_override=True
                # )

                # times_iv = result_iv[0]
                # voltage_iv = result_iv[1]
                # currents_iv = result_iv[2]
                
                # plt.figure()
                # plt.plot(voltage_iv, currents_iv)
                # plt.xlabel("Voltage (V)")
                # plt.ylabel("Current (A)")
                # plt.show()
                
                # print(f'Finished IV sweep for {gtarget*1e9:.4g} nS.')

                
            succeed_prg = False
    except KeyboardInterrupt:
        print("Keyboard Interrupt detected. Saving the data...")
        #Close SMUs and Save Data
        b1500.connection.write("CL")
        b1500.save_numpy_to_csv(b1500.test_info, all_data, filename = f"Program-Current-GD")