import numpy as np
import time
import matplotlib.pyplot as plt

def Switch_Test(self, 
                b1500=None, 
                param_name=None,
                SMU_Pair=[1, 2],
                num_loops=2,
                Read_Voltage=.1,
                Max_Pos_Voltage=2,
                Max_Neg_Voltage=-1,
                VStep=0.1,
                ICompSet=1e-3,
                ICompReset=100e-3,
                SaveData=False,
                **overrides):

    # Collect defaults into a dict
    final_params = {
        "SMU_Pair": SMU_Pair,
        "num_loops": num_loops,
        "Read_Voltage": Read_Voltage,
        "Max_Pos_Voltage": Max_Pos_Voltage,
        "Max_Neg_Voltage": Max_Neg_Voltage,
        "VStep": VStep,
        "ICompSet": ICompSet,
        "ICompReset": ICompReset,
        "SaveData": SaveData
    }

    # Load from parameters if specified
    if b1500 and param_name:
        param_block = dict(b1500.parameters.get(param_name, {}))
        param_block.update(overrides)
        for key, value in param_block.items():
            setattr(b1500, f"{key}_{param_name}", value)
        final_params.update(param_block)

    if not b1500 or not param_name:
        final_params.update(overrides)

    # Unpack final parameters
    SMU_Pair        = final_params["SMU_Pair"]
    SaveData        = final_params["SaveData"]
    ICompSet        = final_params["ICompSet"]
    ICompReset      = final_params["ICompReset"]
    Read_Voltage    = final_params["Read_Voltage"]
    Max_Neg_Voltage = final_params["Max_Neg_Voltage"]
    Max_Pos_Voltage = final_params["Max_Pos_Voltage"]
    VStep           = final_params["VStep"]


    try:
        #
        # Sweep Setup
        #
        positive_sweep = np.concatenate([
            np.arange(0, Max_Pos_Voltage + VStep, VStep),
            np.arange(Max_Pos_Voltage - VStep, -VStep, -VStep)
        ])
        negative_sweep = np.concatenate([
            np.arange(0 - VStep, Max_Neg_Voltage - VStep, -VStep),
            np.arange(Max_Neg_Voltage + VStep, VStep, VStep)
        ])
        full_voltage_sweep = np.concatenate([positive_sweep, negative_sweep])
        num_points = 4 * 101 

        # Preallocate data: voltages in first column
        IVData = np.zeros((num_points, num_loops + 1))  # Don't assign voltages here anymore
        Memory_Windows = []
        

        #
        # Looping
        #
        for loopnumber in range(num_loops):
            currents = []

            # --- Positive Sweep ---
            # for v in full_voltage_sweep[:len(positive_sweep)]:
            #     self.smu_meas_sample(SMU_Pair[0], vmeas=v, icomp=ICompSet,
            #                          interval=10e-3, pre_bias_time=0, number=1,
            #                          disconnect_after=True)
            #     data = b1500.connection.read()
            #     data = b1500.data_clean(b1500, data, b1500.test_info.parameters, NoSave=True)
            #     Current = abs(data.get(f"SMU{SMU_Pair[0]}_Current", None).astype(float)).item()
            #     currents.append(Current)
            #     print(f"Voltage: {v}")
            #     print(f"Conductance: {Current/v}")
            #     if v >= 5 and Current < 10e-9:
            #         print(f"[FAIL] Current < 10nA: {Current} A at V={v}V (Positive sweep, Loop {loopnumber + 1})")
            #         b1500.connection.write("CL")
            #         IVData[:, loopnumber + 1] = np.pad(currents, (0, num_points - len(currents)), 'constant')
            #         if SaveData is True:
            #             b1500.save_numpy_to_csv(b1500.test_info, IVData, filename="SwitchingDataIVFailed")
            #         b1500.connection.write("CL")
            #         return False
            results_pos = self.IVSweep(b1500=b1500, 
                        param_name=None,
                        smu_nums = SMU_Pair[0],
                        vstart=0,
                        vstop=Max_Pos_Voltage,
                        icomp=ICompSet,
                        nsteps=101,
                        connect_first=True,
                        disconnect_after=True,
                        plot_data = False,
                        PULSED_SWEEP = False,
                        mode = 3)
            times = results_pos[0]
            voltages_pos = results_pos[1]
            currents_pos = results_pos[2]

            #
            # Set Read Measurement
            #
            # self.bias_smu(SMU_Pair[1], 0, ICompSet)
            # self.smu_meas_sample(SMU_Pair[0], vmeas=Read_Voltage, icomp=ICompSet,
            #                     interval=10e-3, pre_bias_time=100e-3, number=1,
            #                     disconnect_after=True)
            # data = b1500.connection.read()
            # data = b1500.data_clean(b1500, data, b1500.test_info.parameters, NoSave=True)
            # Initial_Read = abs(data.get(f"SMU{SMU_Pair[0]}_Current", None).astype(float)).item()
            
            results = self.IVSweep(b1500=b1500, 
                        param_name=None,
                        smu_nums = SMU_Pair[0],
                        vstart=0,
                        vstop=Read_Voltage,
                        icomp=ICompReset,
                        nsteps=101,
                        connect_first=True,
                        disconnect_after=True,
                        plot_data = False,
                        PULSED_SWEEP = False,
                        mode = 3)
            times = results[0]
            voltages = results[1]
            currents = results[2]
            vmax_ind = np.argmax(abs(voltages))
            R_last_point = voltages[vmax_ind] / currents[vmax_ind]
            Initial_Read = currents[vmax_ind]
            print( f"Resistance at {voltages[vmax_ind]:.4g} V:    {R_last_point/1e3:.4g} kOhm" ) 
            print( f"Conductance at {voltages[vmax_ind]:.4g} V:    {(1/R_last_point)*1e6:.4g} uS" )

            # --- Negative Sweep ---
            # for v in full_voltage_sweep[len(positive_sweep):]:
            #     self.smu_meas_sample(SMU_Pair[0], vmeas=v, icomp=ICompReset,
            #                          interval=10e-3, pre_bias_time=0, number=1,
            #                          disconnect_after=True)
            #     data = b1500.connection.read()
            #     data = b1500.data_clean(b1500, data, b1500.test_info.parameters, NoSave=True)
            #     Current = abs(data.get(f"SMU{SMU_Pair[0]}_Current", None).astype(float)).item()
            #     currents.append(Current)
            #     print(f"Voltage: {v}")
            #     print(f"Conductance: {Current/v}")
                
            #     if v <= -5 and Current < 10e-9:
            #         print(f"[FAIL] Current < 10nA: {Current} A at V={v}V (Negative sweep, Loop {loopnumber + 1})")
            #         b1500.connection.write("CL")
            #         IVData[:, loopnumber + 1] = np.pad(currents, (0, num_points - len(currents)), 'constant')
            #         if SaveData is True:
            #             b1500.save_numpy_to_csv(b1500.test_info, IVData, filename="SwitchingDataIVFailed")
            #         b1500.connection.write("CL")
            #         return False
            
            results_neg = self.IVSweep(b1500=b1500, 
                        param_name=None,
                        smu_nums = SMU_Pair[0],
                        vstart=0,
                        vstop=Max_Neg_Voltage,
                        icomp=ICompReset,
                        nsteps=101,
                        connect_first=True,
                        disconnect_after=True,
                        plot_data = False,
                        PULSED_SWEEP = False,
                        mode = 3)
            
            voltages_neg = results_neg[1]
            currents_neg = results_neg[2]
            
            # Reverse negative sweep so it goes from most negative to 0
            voltages_neg = voltages_neg[::-1]
            currents_neg = currents_neg[::-1]

            # Concatenate: Negative sweep first, then positive
            full_sweep_voltages = np.concatenate((voltages_neg, voltages_pos))
            full_sweep_currents = np.concatenate((currents_neg, currents_pos))
            
            # Store into IVData
            if loopnumber == 0:
                IVData[:, 0] = full_sweep_voltages  # Set voltages only once  # Only needs to be done once if voltages are the same across loops
            IVData[:, loopnumber + 1] = full_sweep_currents
            # --- Memory Window Check ---
            # self.smu_meas_sample(SMU_Pair[0], vmeas=Read_Voltage, icomp=ICompSet,
            #                      interval=10e-3, pre_bias_time=0, number=1,
            #                      disconnect_after=True)
            # data = b1500.connection.read()
            # data = b1500.data_clean(b1500, data, b1500.test_info.parameters, NoSave=True)
            
            results = self.IVSweep(b1500=b1500, 
                        param_name=None,
                        smu_nums = SMU_Pair[0],
                        vstart=0,
                        vstop=Read_Voltage,
                        icomp=ICompReset,
                        nsteps=101,
                        connect_first=True,
                        disconnect_after=True,
                        plot_data = False,
                        PULSED_SWEEP = False,
                        mode = 3)
            times = results[0]
            voltages = results[1]
            currents = results[2]
            vmax_ind = np.argmax(abs(voltages))
            R_last_point = voltages[vmax_ind] / currents[vmax_ind]
            print( f"Resistance at {voltages[vmax_ind]:.4g} V:    {R_last_point/1e3:.4g} kOhm" ) 
            print( f"Conductance at {voltages[vmax_ind]:.4g} V:    {(1/R_last_point)*1e6:.4g} uS" )
            
            Final_Read = currents[vmax_ind]
            Memory_Window = (Final_Read / Initial_Read) 
            print(f"\n\n\nMemory Window of sweep {loopnumber} is: {Memory_Window}")
            print(f"Set conductance of {Final_Read / Read_Voltage}. Reset Conductance of {Initial_Read / Read_Voltage}\n\n\n")
            Memory_Windows.append(Memory_Window)

            if Memory_Window <= 0.25:
                print(f"[FAIL] Memory Window too small: {Memory_Window}")
                b1500.connection.write("CL")
                if Memory_Windows is not int:
                    for loopnumber in Memory_Windows:
                        print(f"Memory Window of sweep {loopnumber} is: {Memory_Windows[loopnumber]}")
                    if SaveData is True:
                        b1500.save_numpy_to_csv(b1500.test_info, IVData, filename="SwitchingDataIVFailed")
                    b1500.connection.write("CL")
                    return False
                else:
                    print(f"Memory Window of sweep 1 is: {Memory_Windows}")
                    if SaveData is True:
                        b1500.save_numpy_to_csv(b1500.test_info, IVData, filename="SwitchingDataIVFailed")
                    b1500.connection.write("CL")
                    return False
                
            
            # Store all current values in the respective loop column
            IVData[:, loopnumber + 1] = np.array(currents)
            
        b1500.connection.write("CL")
        #
        # Final Save and Plot
        #
        # Final Save and Plot
        print("[SUCCESS] All loops completed. Saving data and plotting results.")
        if SaveData is True:
            b1500.save_numpy_to_csv(b1500.test_info, IVData, filename="SwitchingDataIVSuccess")
    
        for loopnumber in range(num_loops):
            print(f"Memory Window of sweep {loopnumber} is: {Memory_Windows[loopnumber]}")
    
        # Sort the voltage and associated current data for plotting
        sort_indices = np.argsort(IVData[:, 0])  # Sort voltages from lowest to highest
    
        plt.figure(figsize=(7, 5))
        for i in range(1, num_loops + 1):
            sorted_voltages = IVData[sort_indices, 0]
            sorted_currents = IVData[sort_indices, i]
            plt.plot(sorted_voltages, sorted_currents, label=f'Loop {i}', marker='o', linestyle='-')
    
        plt.xlabel('Voltage (V)')
        plt.ylabel('Current (A)')
        plt.title(f'I-V Curves for {num_loops} Loop(s)')
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()
        
        return True
    except KeyboardInterrupt as e:
        if SaveData is True:
            b1500.save_numpy_to_csv(b1500.test_info, IVData, filename="SwitchingDataIVStopped")
        b1500.connection.write("CL")

    