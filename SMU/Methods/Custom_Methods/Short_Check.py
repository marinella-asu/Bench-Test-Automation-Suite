import numpy as np
import time

#This Function Returns a True/False Boolean on whether we can find a short between two SMUs given these parameters:
def Short_Check(self, 
                b1500=None, 
                param_name=None,
                SMU_Pair=[1, 2],                # These are the SMUs we'll use to check if they're shorted, format: [smu#, smu#] the second smu is grounded
                Max_Resistance=200,             # Maximum resistance (Ohms) to still consider the path a "short"
                Max_Voltage=1,                  # Maximum voltage applied during the short check
                IComp=1e-3, 
                Dynamic_Check=False,           # If True, ramps voltage instead of applying it directly
                D_StartV=0,                     # (Dynamic only) Starting voltage of ramp
                D_Step=0.5,                     # (Dynamic only) Step size of voltage ramp
                D_Wait=10,                      # (Dynamic only) Wait time between voltage steps
                SaveData = False,
                **overrides):                  # Manual per-call overrides (e.g. D_Wait=5)

    # Collect defaults into a dict
    final_params = {
        "SMU_Pair": SMU_Pair,
        "Max_Resistance": Max_Resistance,
        "Max_Voltage": Max_Voltage,
        "IComp": IComp,
        "Dynamic_Check": Dynamic_Check,
        "D_StartV": D_StartV,
        "D_Step": D_Step,
        "D_Wait": D_Wait,
        "SaveData": SaveData
    }

    
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
        

            
    # Unpack everything for use
    SMU_Pair       = final_params["SMU_Pair"]
    Max_Resistance = final_params["Max_Resistance"]
    Max_Voltage    = final_params["Max_Voltage"]
    IComp          = final_params["IComp"]
    Dynamic_Check  = final_params["Dynamic_Check"]
    D_StartV       = final_params["D_StartV"]
    D_Step         = final_params["D_Step"]
    D_Wait         = final_params["D_Wait"]
    SaveData       = final_params["SaveData"]

    #
    #
    # This is where the actual logic starts
    #
    #

    try:
        Measured_SMU = b1500.smus[SMU_Pair[0] - 1] #Channel Number
        Grounded_SMU = b1500.smus[SMU_Pair[1] - 1] #Channel Number

        SavedData = np.empty((0, 2))
        
        if Dynamic_Check:
            while D_StartV <= Max_Voltage: 
                start_time = time.time()
                while (time.time() - start_time) < D_Wait:
                    b1500.smu.connect_smu_list(SMU_Pair)

                    # Set measurement format
                    b1500.connection.write("FMT 1,1") 
                    # Select high-resolution ADC
                    b1500.connection.write(f"AAD {Measured_SMU}, 1") 
                    # Set Current Measurement
                    b1500.connection.write(f"CMM {Measured_SMU},1")

                    b1500.connection.write(f"DV {Measured_SMU}, 0, {D_StartV}, {IComp}") #Here We setup our bias we are going to apply which will update after we reach D_Wait
                    b1500.connection.write(f"DV {Grounded_SMU}, 0, 0, {IComp}")

                    b1500.connection.write(f"MM 1, {Measured_SMU}")

                    b1500.connection.write("XE") #Start measurement

                    data = b1500.connection.read()
                    data = b1500.data_clean(b1500, data, b1500.test_info.parameters, NoSave = True)
                    Current = data.get(f"SMU{SMU_Pair[0]}_Current", None)
                    Current = abs(Current.astype(float)).item()
                        
                    Resistance = abs(D_StartV / Current)
                    print(f"Resistance: {Resistance}")
                    print(f"Voltage: {D_StartV}")
                    print(f"Current: {Current}")
                    if SaveData is True:
                        new_data = [Current, D_StartV]

                        # Append along axis 0 (rows)
                        SavedData = np.append(SavedData, [new_data], axis=0)
                    if Resistance < Max_Resistance:
                        if SaveData is True:
                            b1500.save_numpy_to_csv(b1500.test_info, SavedData, filename = "FormingDataIV")
                        b1500.connection.write("CL")
                        return True


                if D_StartV >= Max_Voltage-.0001:
                    b1500.save_numpy_to_csv(b1500.test_info, SavedData, filename = "FormingDataIVFailed")
                    b1500.connection.write("CL")
                    return False
                D_StartV += D_Step
            
        else:
            for i in range(11):
                b1500.smu.connect_smu_list(SMU_Pair)
                # Set measurement format
                b1500.connection.write("FMT 1,1") 
                # Select high-resolution ADC
                b1500.connection.write(f"AAD {Measured_SMU}, 1") 
                # Set Current Measurement
                b1500.connection.write(f"CMM {Measured_SMU},1")

                b1500.connection.write(f"DV {Measured_SMU}, 0, {Max_Voltage}, 100e-3") #Here We setup our bias we are going to apply which will update after we reach D_Wait
                b1500.connection.write(f"DV {Grounded_SMU}, 0, 0, 100e-3")

                b1500.connection.write(f"MM 1, {Measured_SMU}")

                b1500.connection.write("XE") #Start measurement

                data = b1500.connection.read()
                data = b1500.data_clean(b1500, data, b1500.test_info.parameters, NoSave = True)
                Current = data.get(f"SMU{SMU_Pair[0]}_Current", None)
                Current = Current.astype(float)
                Resistance = Max_Voltage / Current

                if Resistance < Max_Resistance:
                    b1500.connection.write("CL")
                    return True
            
            b1500.connection.write("CL")
            return False
    except KeyboardInterrupt as e:
        if SavedData is not None:
            b1500.save_numpy_to_csv(b1500.test_info, SavedData, filename = "FormingDataIVStopped")
        b1500.connection.write("CL")
