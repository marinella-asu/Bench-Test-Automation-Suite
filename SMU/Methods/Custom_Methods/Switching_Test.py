import numpy as np
import time
import matplotlib.pyplot as plt

def Switch_Test(self, 
                b1500=None, 
                param_name=None,
                SMU_Pair=[1, 2],
                num_loops=10,
                Read_Voltage=1,
                Max_Pos_Voltage=12,
                Max_Neg_Voltage=-10,
                VStep=0.1,
                IComp=100e-3,
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
        "IComp": IComp,
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
    IComp           = final_params["IComp"]
    Read_Voltage    = final_params["Read_Voltage"]
    Max_Neg_Voltage = final_params["Max_Neg_Voltage"]
    Max_Pos_Voltage = final_params["Max_Pos_Voltage"]
    VStep           = final_params["VStep"]

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
    num_points = len(full_voltage_sweep)

    # Preallocate data: voltages in first column
    IVData = np.zeros((num_points, num_loops + 1))
    IVData[:, 0] = full_voltage_sweep

    #
    # Initial Read Measurement
    #
    self.smu_meas_sample(SMU_Pair[0], vmeas=Read_Voltage, icomp=IComp,
                         interval=10e-3, pre_bias_time=100e-3, number=1,
                         disconnect_after=True, plot_results=False)
    data = b1500.connection.read()
    data = b1500.data_clean(b1500, data, b1500.test_info.parameters, NoSave=True)
    Initial_Read = abs(data.get(f"SMU{SMU_Pair[0]}_Current", None).astype(float)).item()

    #
    # Looping
    #
    for loopnumber in range(num_loops):
        currents = []

        # --- Positive Sweep ---
        for v in full_voltage_sweep[:len(positive_sweep)]:
            self.smu_meas_sample(SMU_Pair[0], vmeas=v, icomp=IComp,
                                 interval=10e-3, pre_bias_time=100e-3, number=1,
                                 disconnect_after=True, plot_results=False)
            data = b1500.connection.read()
            data = b1500.data_clean(b1500, data, b1500.test_info.parameters, NoSave=True)
            Current = abs(data.get(f"SMU{SMU_Pair[0]}_Current", None).astype(float)).item()
            currents.append(Current)

            if v >= 5 and Current < 10e-9:
                print(f"[FAIL] Current < 10nA: {Current} A at V={v}V (Positive sweep, Loop {loopnumber + 1})")
                IVData[:, loopnumber + 1] = np.pad(currents, (0, num_points - len(currents)), 'constant')
                if SaveData is True:
                    b1500.save_numpy_to_csv(b1500.test_info, IVData, filename="SwitchingDataIVFailed")
                return False

        # --- Memory Window Check ---
        self.smu_meas_sample(SMU_Pair[0], vmeas=Read_Voltage, icomp=IComp,
                             interval=10e-3, pre_bias_time=100e-3, number=1,
                             disconnect_after=True, plot_results=False)
        data = b1500.connection.read()
        data = b1500.data_clean(b1500, data, b1500.test_info.parameters, NoSave=True)
        Final_Read = abs(data.get(f"SMU{SMU_Pair[0]}_Current", None).astype(float)).item()
        Memory_Window = Final_Read / Initial_Read

        if Memory_Window <= 0.5:
            print(f"[FAIL] Memory Window too small: {Memory_Window}")
            if SaveData is True:
                b1500.save_numpy_to_csv(b1500.test_info, IVData, filename="SwitchingDataIVFailed")
            return False

        # --- Negative Sweep ---
        for v in full_voltage_sweep[len(positive_sweep):]:
            self.smu_meas_sample(SMU_Pair[0], vmeas=v, icomp=IComp,
                                 interval=10e-3, pre_bias_time=100e-3, number=1,
                                 disconnect_after=True, plot_results=False)
            data = b1500.connection.read()
            data = b1500.data_clean(b1500, data, b1500.test_info.parameters, NoSave=True)
            Current = abs(data.get(f"SMU{SMU_Pair[0]}_Current", None).astype(float)).item()
            currents.append(Current)

            if v <= -5 and Current < 10e-9:
                print(f"[FAIL] Current < 10nA: {Current} A at V={v}V (Negative sweep, Loop {loopnumber + 1})")
                IVData[:, loopnumber + 1] = np.pad(currents, (0, num_points - len(currents)), 'constant')
                if SaveData is True:
                    b1500.save_numpy_to_csv(b1500.test_info, IVData, filename="SwitchingDataIVFailed")
                return False

        # Store all current values in the respective loop column
        IVData[:, loopnumber + 1] = np.array(currents)

    #
    # Final Save and Plot
    #
    print("[SUCCESS] All loops completed. Saving data and plotting results.")
    if SaveData is True:
        b1500.save_numpy_to_csv(b1500.test_info, IVData, filename="SwitchingDataIVSuccess")

    # Plot all loops
    plt.figure(figsize=(7, 5))
    for i in range(1, num_loops + 1):
        plt.plot(IVData[:, 0], IVData[:, i], label=f'Loop {i}', marker='o', linestyle='-')

    plt.xlabel('Voltage (V)')
    plt.ylabel('Current (A)')
    plt.title(f'I-V Curves for {num_loops} Loop(s)')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()
