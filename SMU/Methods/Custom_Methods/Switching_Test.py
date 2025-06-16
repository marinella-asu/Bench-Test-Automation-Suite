import numpy as np
import time
import matplotlib.pyplot as plt

def Switch_Test(self, 
                b1500=None, 
                param_name=None,
                SMU_Pair=[1, 2],
                num_loops=2,
                Read_Voltage=.1,
                Pos_Voltage=2,
                Neg_Voltage=-1,
                VStep=0.1,
                ICompSet=1e-3,
                ICompReset=100e-3,
                ICompRead = 100e-3,
                SaveData=True,
                Reset_Voltage_Step =.1,
                Min_MemWindow = 1.1,
                
                **overrides):

    # Collect defaults into a dict
    final_params = {
        "SMU_Pair": SMU_Pair,
        "num_loops": num_loops,
        "Read_Voltage": Read_Voltage,
        "Pos_Voltage": Pos_Voltage,
        "Neg_Voltage": Neg_Voltage,
        "VStep": VStep,
        "ICompSet": ICompSet,
        "ICompReset": ICompReset,
        "ICompRead": ICompRead,
        "SaveData": SaveData,
        "Reset_Voltage_Step": Reset_Voltage_Step,
        "Min_MemWindow": Min_MemWindow,
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
    num_loops       = final_params["num_loops"]
    SaveData        = final_params["SaveData"]
    ICompSet        = final_params["ICompSet"]
    ICompReset      = final_params["ICompReset"]
    ICompRead       = final_params["ICompRead"]
    Read_Voltage    = final_params["Read_Voltage"]
    Neg_Voltage = final_params["Neg_Voltage"]
    Pos_Voltage = final_params["Pos_Voltage"]
    VStep           = final_params["VStep"]
    Reset_Voltage_Step=final_params["Reset_Voltage_Step"]
    Min_MemWindow   = final_params["Min_MemWindow"]


    try:
        #
        # Sweep Setup
        #
        positive_sweep = np.concatenate([
            np.arange(0, Pos_Voltage + VStep, VStep),
            np.arange(Pos_Voltage - VStep, -VStep, -VStep)
        ])
        negative_sweep = np.concatenate([
            np.arange(0 - VStep, Neg_Voltage - VStep, -VStep),
            np.arange(Neg_Voltage + VStep, VStep, VStep)
        ])
        full_voltage_sweep = np.concatenate([positive_sweep, negative_sweep])
        num_points = 4 * 101 

        # Preallocate data: voltages in first column
        IVData = np.zeros((num_points, num_loops + 1))  # Don't assign voltages here anymore
        Memory_Windows = []
        

        #
        # Looping
        #
        looping = True
        while looping:
            for loopnumber in range(num_loops):
                int(loopnumber)
                currents = []
                restart = False
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
                            vstop=Pos_Voltage,
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
                vind = np.argmax(abs(voltages))
                R_last_point = voltages[vind] / currents[vind]
                Initial_Read = currents[vind]
                print( f"Resistance at {voltages[vind]:.4g} V:    {R_last_point/1e3:.4g} kOhm" ) 
                print( f"Conductance at {voltages[vind]:.4g} V:    {(1/R_last_point)*1e6:.4g} uS" )

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
                            vstop=Neg_Voltage,
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
                currents_neg = abs(currents_neg[::-1])

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
                vind = np.argmax(abs(voltages))
                R_last_point = voltages[vind] / currents[vind]
                print( f"Resistance at {voltages[vind]:.4g} V:    {R_last_point/1e3:.4g} kOhm" ) 
                print( f"Conductance at {voltages[vind]:.4g} V:    {(1/R_last_point)*1e6:.4g} uS" )
                
                Final_Read = currents[vind]
                Memory_Window = (Initial_Read / Final_Read) 
                print(f"\n\n\nMemory Window of sweep {loopnumber} is: {Memory_Window}")
                print(f"Set conductance of {Initial_Read / Read_Voltage}. Reset Conductance of {Final_Read / Read_Voltage}\n\n\n")
                Memory_Windows.append(Memory_Window)

                if Memory_Window <= Min_MemWindow:
                    print(f"[FAIL] Memory Window too small: {Memory_Window}")
                    b1500.connection.write("CL")
                    if abs(Final_Read) <= 1e-9:
                        print("\n\nThe Device IS DEAD!!!!!!!!!!!!!!!!\n\n")
                    if Memory_Windows is not int:
                        for loopnumber in range(len(Memory_Windows)):
                            print(f"Memory Window of sweep {loopnumber} is: {Memory_Windows[int(loopnumber)]}")
                        if SaveData is True:
                            headers = ["Voltage (V)"] + [f"Loop {i+1} (A)" for i in range(num_loops)]
                            b1500.save_numpy_to_csv(b1500, IVData, filename="SwitchingDataIVFailed", headers=headers)
                        b1500.connection.write("CL")
                        Neg_Voltage -= Reset_Voltage_Step
                        restart = True
                        if abs(Final_Read) <= 1e-9:
                            print("Exiting because of dead device")
                            exit(1)
                        break
                        
                    else:
                        print(f"Memory Window of sweep 1 is: {Memory_Windows}")
                        if SaveData is True:
                            headers = ["Voltage (V)"] + [f"Loop {i+1} (A)" for i in range(num_loops)]
                            b1500.save_numpy_to_csv(b1500, IVData, filename="SwitchingDataIVFailed", headers=headers)
                        b1500.connection.write("CL")
                        Neg_Voltage -= Reset_Voltage_Step
                        restart = True
                        if abs(Final_Read) <= 1e-9:
                            print("Exiting because of dead device")
                            exit(1)
                        break
                    
                # print(f"IVDATA: {IVData}")
                # print(f"Currents: {currents}")
                
            b1500.connection.write("CL")
            #
            # Final Save and Plot
            #
            # Final Save and Plot
            print("[SUCCESS] All loops completed. Saving data and plotting results.")
            looping = False
            if restart:
                looping = True
                continue
            if SaveData is True:
                headers = ["Voltage (V)"] + [f"Loop {i+1} (A)" for i in range(num_loops)]
                b1500.save_numpy_to_csv(b1500, IVData, filename="SwitchingDataIVSuccess", headers=headers)
        
            for loopnumber in range(num_loops):
                print(f"Memory Window of sweep {loopnumber+1} is: {Memory_Windows[int(loopnumber)]}")
        
            plt.figure(figsize=(7, 5))
            for i in range(1, num_loops + 1):
               voltages = IVData[:, 0]
               currents = IVData[:, i]
               plt.plot(voltages, currents, label=f'Loop {i}', linestyle='-')  # No markers
            
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
            headers = ["Voltage (V)"] + [f"Loop {i+1} (A)" for i in range(num_loops)]
            b1500.save_numpy_to_csv(b1500, IVData, filename="SwitchingDataIVStopped", headers=headers)
        b1500.connection.write("CL")

    