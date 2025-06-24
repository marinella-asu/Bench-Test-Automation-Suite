import time
import numpy as np
import matplotlib.pyplot as plt

def ReRamRetention(self, 
                b1500=None,  #Required
                param_name=None, #Required
                SMU_Pair=[1, 2],
                ReadVoltage = .1,
                ReadCompliance = 100e-3,
                Interval = 10e-3,
                Duration = 10, #Length of Retention Test in Seconds
                SampleRate = 60, #Measurements per Minute (Linear)
                AlternateRate = "Linear", #Set this To Logarithmic to make it sample ever 10, 10e1, 10e2, 10e3... Seconds
                SaveData = True,
                **overrides):

    # Collect defaults into a dict
    final_params = { #Required
        "SMU_Pair": SMU_Pair,
        "ReadVoltage": ReadVoltage,
        "ReadCompliance": ReadCompliance,
        "Interval": Interval,
        "Duration": Duration,
        "SampleRate": SampleRate,
        "AlternateRate": AlternateRate,
        "SaveData": SaveData,
    }

    #Required
    # If we were given b1500 + param_name, load values from parameters
    if b1500 and param_name:
        param_block = dict(b1500.parameters.get(param_name, {}))
        param_block.update(overrides)  # Apply runtime overrides

        # Attach as individual attributes to b1500 for global access
        for key, value in param_block.items():
            setattr(b1500, f"{key}_{param_name}", value)

        # Merge values from parameters with existing defaults
        final_params.update(param_block)

    # If we didn’t use parameters at all (case 3), just apply overrides directly
    if not b1500 or not param_name:
        final_params.update(overrides)
        

            
    # Unpack everything for use #Required
    SMU_Pair       = final_params["SMU_Pair"]
    ReadVoltage    = final_params["ReadVoltage"]
    ReadCompliance = final_params["ReadCompliance"]
    Interval       = final_params["Interval"]
    Duration       = final_params["Duration"]
    SampleRate     = final_params["SampleRate"]
    AlternateRate  = final_params["AlternateRate"] 
    SaveData       = final_params["SaveData"]




    #Logic Starts
    try:
        Measured_SMU = b1500.smus[SMU_Pair[0] - 1] #Channel Number
        Grounded_SMU = b1500.smus[SMU_Pair[1] - 1] #Channel Number
        SavedData = np.empty((0, 2))

        b1500.smu.connect_smu_list(SMU_Pair)

        if AlternateRate is not "Linear":
            ExponentCounter = 0

        start_time = time.time()
        while (time.time() - start_time) < Duration:
            if AlternateRate is "Linear":
                time.sleep(60/SampleRate)
            else: 
                time.sleep(10 ** ExponentCounter)
                ExponentCounter += 1
            
            b1500.connection.write(f"DV {Grounded_SMU}, 0, 0, {ReadCompliance}")
            data = self.smu_meas_sample(b1500, SMU_Pair[0], vmeas = ReadVoltage, icomp = ReadCompliance, interval = Interval, disconnect_after = False)

            data = b1500.data_clean(b1500, data, b1500.test_info.parameters, NoSave = True)
            Current = data.get(f"SMU{SMU_Pair[0]}_Current", None)
            Current = abs(Current.astype(float)).item()

            Resistance = abs(ReadVoltage / Current)
            Conductance = (1/ Resistance) * 1e6
            print(f"Conductance: {Conductance} uS")
            print(f"Voltage: {ReadVoltage}")
            print(f"Current: {Current}")
            print(f"Resistance: {Resistance}")

            if SaveData is True:
                new_data = [time.time() - start_time, Conductance]
                SavedData = np.append(SavedData, [new_data], axis=0)

        b1500.connection.write("CL")

        if SaveData is True:
            b1500.save_numpy_to_csv(b1500, SavedData, filename = "RetentionData", headers = ["Time (s)", "Conductance (uS)"])
            
            plt.plot(SavedData[:, 0], SavedData[:, 1], label=f'Retention over {Duration}', marker='o', linestyle='-')
            plt.xlabel('Time (s)')
            plt.ylabel('Conductance (uS)')
            plt.title(f'Retention: Conductance over Time')
            plt.grid(True)
            plt.legend()
            plt.tight_layout()
            plt.show()

    except KeyboardInterrupt as e:
        if SavedData is not None:
            b1500.save_numpy_to_csv(b1500, SavedData, filename = "RetentionDataStopped", headers = ["Time (s)", "Conductance (uS)"])
        b1500.connection.write("CL")

        