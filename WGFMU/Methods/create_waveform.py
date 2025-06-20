import ctypes as ct
import time  # Import time module for performance tracking
from time import perf_counter
import os
import wgfmu_consts as wgc  # Import constants for WGFMU operations
import pandas as pd
import numpy as np

def create_waveform(self, b1500, patt_name="", alternate_waveform = None, OverrideValue = None, num_copies = 1, meas_pts1=1, meas_interval1=1):
        # drive data: tuple, (time , voltage) , both numpy vectors
        # ranging data: tuple ( time , range setting ) , numpy vector and list
        # meas data: tuple (time , Npts , interval , averaging time , mode )
        
        #So make it work for both WGFMU CHANNELS so we need the data to pass in for both VDD and VSS

        #Drive data needs to be t, v, t, v lets do VDD then VSS


        # THIS IS ONLY FOR USING AN ALTERNATE WAVEFORM
        # IF YOUR LOOKING FOR THE USUAL USE CASE ITS BELOW THIS IF STATEMENT
        # |
        # |
        # |  Condense this if statement if you aren't looking for alternate waveforms
        # V  
        if alternate_waveform is not None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            while not script_dir.endswith("Bench-Test-Automation-Suite-main"):
                script_dir = os.path.dirname(script_dir)  # Move up one level

            # Ensure the data is stored inside "Bench_Test_Automation_Suite/Data"
            waveform_data_path = os.path.join(script_dir, "Waveforms", f"{alternate_waveform}.txt")
            if os.path.exists(waveform_data_path):
                with open(waveform_data_path, "r") as f:
                    VDD_data = [line.strip() for line in f.readlines()]
                # print(f"✅ Loaded waveform from {waveform_data_path}")
            
            labels = []
            times = []
            vdd_voltage = []
            vss_voltage = []
            compliance = []
            
            for line in VDD_data:
                parts = line.split(",")
                label = str(parts[0])
                time1 = float(parts[1])
                vdd_val= float(parts[2])
                comp = str(parts[4]) if len(parts) > 4 else ""
                vss_val = float(parts[3])


                if OverrideValue is not None:
                    for key, value in OverrideValue:
                        if key.lower() == "comp":
                            comp = str(value)
                        elif key.lower() == "program" and "program" in label.lower():
                            vdd_val = float(value)
                        elif key.lower() == "read" and "read" in label.lower():
                            vdd_val = float(value)
                
                
                labels.append(label)
                times.append(time1)
                vdd_voltage.append(vdd_val)
                vss_voltage.append(vss_val)
                compliance.append(comp)
                
            
            VDD_time = []
            VDD_voltage = []
            VSS_time = []
            VSS_voltage = []
            compliance_literals = []
            compliance_time = []
            compliance_data = []
            meas_times = []
            meas_pts = []
            meas_interval = []
            meas_averaging = []
            meas_mode = []
                
            
            # print("Labels:", labels)
            # print("Times:", times)
            # print("VDD:", vdd_voltage)
            # print("VSS:", vss_voltage)
            # print("Compliance:", compliance)
            
            trd = b1500.trd
            pts_per_meas = b1500.pts_per_meas
            for time_entry, vdd_entry, vss_entry, label_entry, comp_entry in zip(times, vdd_voltage, vss_voltage, labels, compliance):
                time_val = time_entry 
                vdd_val = vdd_entry  
                vss_val = vss_entry
                label_val = str((label_entry)).lower()  # Convert label to lowercase for searching
                comp_val = str(comp_entry).lower()
            
                # If VDD is NOT "X", store time and voltage for VDD
                if vdd_val != "X":
                    VDD_time.append(time_val)
                    VDD_voltage.append(float(vdd_val))

                # If VSS is NOT "X", store time and voltage for VSS
                if vss_val != "X":
                    VSS_time.append(time_val)
                    VSS_voltage.append(float(vss_val))

                # Handle compliance
                if "comp" in label_val:
                    compliance_time.append(time_val)
                    if comp_val == "1ua" or comp_val == "6001":
                        compliance_data.append((wgc.WGFMU_MEASURE_CURRENT_RANGE_1UA))
                    elif comp_val == "10ua" or comp_val == "6002":
                        compliance_data.append((wgc.WGFMU_MEASURE_CURRENT_RANGE_10UA))
                    elif comp_val == "100ua" or comp_val == "6003":
                        compliance_data.append((wgc.WGFMU_MEASURE_CURRENT_RANGE_100UA))
                    elif comp_val == "1ma" or comp_val == "6004":
                        compliance_data.append((wgc.WGFMU_MEASURE_CURRENT_RANGE_1MA))
                    elif comp_val == "10ma" or comp_val == "6005":
                        compliance_data.append((wgc.WGFMU_MEASURE_CURRENT_RANGE_10MA))
                    else:
                        print(f"UNKNOWN COMPLIANCE VALUE INPUT: {comp_val}\n##########################\n")
                    

                # Handle measurement events
                if "meas" in label_val:
                    meas_times.append(time_val)
                    meas_pts.append(meas_pts1)  # Default is 1
                    meas_interval.append(meas_interval1)  # Reading duration
                    meas_averaging.append(trd / 2)  # Averaging period
                    meas_mode.append(wgc.WGFMU_MEASURE_EVENT_DATA_AVERAGED)  # Default averaged mode

            # Save the cleaned-up waveform data
            waveform_data = {
                "Labels": [entry for entry in labels],
                "VDD Time": VDD_time,
                "VSS Time": VSS_time,
                "VDD Voltage": VDD_voltage,
                "VSS Voltage": VSS_voltage,
                "Compliance Literals": compliance_literals,
                "Compliance Time": compliance_time,
                "Compliance Data": compliance_data,
                "Measurement Data": [meas_times, meas_pts, meas_interval, meas_averaging, meas_mode]
            }
            
        
            meas_data = waveform_data["Measurement Data"]
            # print(f"measurement data: {meas_data}")
            comp_data = waveform_data["Compliance Data"]
            # print(f"comp data: {comp_data}")
            VDD_waveform = [waveform_data["VDD Time"], waveform_data["VDD Voltage"]]
            VSS_waveform = [waveform_data["VSS Time"], waveform_data["VSS Voltage"]]
            # print(f"VDD data: {VDD_waveform}")
            # print(f"VSS data: {VSS_waveform}")
            timestamp = time.perf_counter()
            if (b1500.test_info.VDD_WGFMU == 1):
                
                vector_names = [ self.cstr((f"ch{channel}_{patt_name}_{timestamp}")) for channel in self.wgfmus]
                # print(f"{vector_names}")
                for ch_ind in range(len(self.wgfmus)):
                    channel = self.wgfmus[ch_ind]
                    vector_name = vector_names[ch_ind]

                    # Create pattern for this channel
                    self.wg.WGFMU_createPattern(vector_name, self.cf(0))

                    # Select waveform data based on channel index
                    if ch_ind == 0:  # First channel (VDD)
                        drive_times = VDD_waveform[0]
                        drive_voltages = VDD_waveform[1]
                    elif ch_ind == 1:  # Second channel (VSS)
                        drive_times = VSS_waveform[0]
                        drive_voltages = VSS_waveform[1]
                    else:
                        print(f"⚠️ Unexpected channel index {ch_ind}, skipping...")
                        continue  # Skip unexpected channels

                    # Apply waveform data to the current channel
                    for time_idx in range(len(drive_times)):
                        time_pt = self.cf(drive_times[time_idx])
                        voltage = self.cf(drive_voltages[time_idx])

                        self.wg.WGFMU_setVector(vector_name, time_pt, voltage)

                    
                    # Add ranging events if they were included
                    if (len(comp_data) > 0):
                        ranging_settings = comp_data
                        
                        for ind in range(len(ranging_settings)):
                            range_time = self.cf(waveform_data["Compliance Time"][ind])
                            range_setting =  ranging_settings[ind]
                            range_event_name = self.cstr( f"ch{channel}_range{ind}_{timestamp}")
                            
                            self.wg.WGFMU_setRangeEvent(vector_name, range_event_name, range_time , range_setting) #as soon as the measurement is done, change the current range we can drive enough current
                            

                    
                    # Add measurement events if they're included
                    if len( meas_data ) > 0 :
                        meas_times = meas_data[0]
                        meas_pts = meas_data[1]
                        meas_intervals = meas_data[2]
                        meas_averaging_times = meas_data[3]
                        meas_modes = meas_data[4]
                        
                        for ind in range(len( meas_times ) ):
                            time_pt = self.cf( meas_times[ind] )
                            points = int( meas_pts[ind] )
                            interval = self.cf( meas_intervals[ind] )
                            averaging_time = self.cf( meas_averaging_times[ind] )
                            mode = int( meas_modes[ind] )
                            meas_event_name = self.cstr( f"ch{channel}_meas{ind}_{timestamp}" )
                            
                            #print( f"{vector_name.value}  {meas_event_name.value}  {time_pt}  {points}  {interval}  {averaging_time}  {mode}")
                            self.wg.WGFMU_setMeasureEvent( vector_name , meas_event_name , time_pt , points , interval , averaging_time , mode )
                    
                        self.wg.WGFMU_addSequence( channel , vector_name , self.cf(num_copies) ) # add copies copies of the pattern "pulse" to the channel
                    
                return vector_name
            else:            
                self.wgfmus = list(reversed(self.wgfmus))
                vector_names = [ self.cstr((f"ch{channel}_{patt_name}_{timestamp}")) for channel in self.wgfmus]
                # print(f"{vector_names}")
                for ch_ind, channel in enumerate(self.wgfmus):
                    vector_name = vector_names[ch_ind]
    
                    # Create pattern for this channel
                    self.wg.WGFMU_createPattern(vector_name, self.cf(0))
    
                    # Select waveform data based on channel index
                    if ch_ind == 0:  # First channel (VDD)
                        drive_times = VDD_waveform[0]
                        drive_voltages = VDD_waveform[1]
                    elif ch_ind == 1:  # Second channel (VSS)
                        drive_times = VSS_waveform[0]
                        drive_voltages = VSS_waveform[1]
                    else:
                        print(f"⚠️ Unexpected channel index {ch_ind}, skipping...")
                        continue  # Skip unexpected channels
    
                    # Apply waveform data to the current channel
                    for time_idx in range(len(drive_times)):
                        time_pt = self.cf(drive_times[time_idx])
                        voltage = self.cf(drive_voltages[time_idx])
    
                        self.wg.WGFMU_setVector(vector_name, time_pt, voltage)
    
                    
                    # Add ranging events if they were included
                    if (len(comp_data) > 0):
                        ranging_settings = comp_data
                        
                        for ind in range(len(ranging_settings)):
                            range_time = self.cf(waveform_data["Compliance Time"][ind])
                            range_setting =  ranging_settings[ind]
                            range_event_name = self.cstr( f"ch{channel}_range{ind}_{timestamp}")
                            
                            self.wg.WGFMU_setRangeEvent(vector_name, range_event_name, range_time , range_setting) #as soon as the measurement is done, change the current range we can drive enough current
                            
    
                    
                    # Add measurement events if they're included
                    if len( meas_data ) > 0 :
                        meas_times = meas_data[0]
                        meas_pts = meas_data[1]
                        meas_intervals = meas_data[2]
                        meas_averaging_times = meas_data[3]
                        meas_modes = meas_data[4]
                        
                        for ind in range(len( meas_times ) ):
                            time_pt = self.cf( meas_times[ind] )
                            points = int( meas_pts[ind] )
                            interval = self.cf( meas_intervals[ind] )
                            averaging_time = self.cf( meas_averaging_times[ind] )
                            mode = int( meas_modes[ind] )
                            meas_event_name = self.cstr( f"ch{channel}_meas{ind}_{timestamp}" )
                            
                            #print( f"{vector_name.value}  {meas_event_name.value}  {time_pt}  {points}  {interval}  {averaging_time}  {mode}")
                            self.wg.WGFMU_setMeasureEvent( vector_name , meas_event_name , time_pt , points , interval , averaging_time , mode )
                    
                        self.wg.WGFMU_addSequence( channel , vector_name , self.cf(num_copies) ) # add copies copies of the pattern "pulse" to the channel
                self.wgfmus = list(reversed(self.wgfmus))
                return vector_name
        
        # # HERES THE NORMAL FUNCTION NOT USING AN ALTERNATE WAVEFORM
        # #
        # #
        # #
        # #
        # #
        # #
        # meas_data = b1500.test_info.waveform_data["Measurement Data"]
        # comp_data = b1500.test_info.waveform_data["Compliance Data"]
        # VDD_waveform = [b1500.test_info.waveform_data["VDD Time"], b1500.test_info.waveform_data["VDD Voltage"]]
        # VSS_waveform = [b1500.test_info.waveform_data["VSS Time"], b1500.test_info.waveform_data["VSS Voltage"]]

        # timestamp = time.perf_counter()
        # if (b1500.test_info.VDD_WGFMU == 1):
        #     vector_names = [ self.cstr( f"ch{channel}_{patt_name}_{timestamp}" ) for channel in self.wgfmus]
        #     for ch_ind, channel in enumerate(self.wgfmus):
        #         vector_name = vector_names[ch_ind]

        #         # Create pattern for this channel
        #         self.wg.WGFMU_createPattern(vector_name, self.cf(0))

        #         # Select waveform data based on channel index
        #         if ch_ind == 0:  # First channel (VDD)
        #             drive_times = VDD_waveform[0]
        #             drive_voltages = VDD_waveform[1]
        #         elif ch_ind == 1:  # Second channel (VSS)
        #             drive_times = VSS_waveform[0]
        #             drive_voltages = VSS_waveform[1]
        #         else:
        #             print(f"⚠️ Unexpected channel index {ch_ind}, skipping...")
        #             continue  # Skip unexpected channels

        #         # Apply waveform data to the current channel
        #         for time_idx in range(len(drive_times)):
        #             time_pt = self.cf(drive_times[time_idx])
        #             voltage = self.cf(drive_voltages[time_idx])

        #             self.wg.WGFMU_setVector(vector_name, time_pt, voltage)

                
        #         # Add ranging events if they were included
        #         if (len(comp_data) > 0):
        #             ranging_times = comp_data[0]
        #             ranging_settings = comp_data[1]
                    
        #             for ind in range(len(ranging_times)):
        #                 range_time = self.cf(ranging_times[ind] )
        #                 range_setting =  ranging_settings[ind] 
        #                 range_event_name = self.cstr( f"ch{channel}_range{ind}_{timestamp}")
                        
        #                 self.wg.WGFMU_setRangeEvent(vector_name, range_event_name, range_time , range_setting) #as soon as the measurement is done, change the current range we can drive enough current
                        

                
        #         # Add measurement events if they're included
        #         if len( meas_data ) > 0 :
        #             meas_times = meas_data[0]
        #             meas_pts = meas_data[1]
        #             meas_intervals = meas_data[2]
        #             meas_averaging_times = meas_data[3]
        #             meas_modes = meas_data[4]
                    
        #             for ind in range(len( meas_times ) ):
        #                 time_pt = self.cf( meas_times[ind] )
        #                 points = int( meas_pts[ind] )
        #                 interval = self.cf( meas_intervals[ind] )
        #                 averaging_time = self.cf( meas_averaging_times[ind] )
        #                 mode = int( meas_modes[ind] )
        #                 meas_event_name = self.cstr( f"ch{channel}_meas{ind}_{timestamp}" )
                        
        #                 #print( f"{vector_name.value}  {meas_event_name.value}  {time_pt}  {points}  {interval}  {averaging_time}  {mode}")
        #                 self.wg.WGFMU_setMeasureEvent( vector_name , meas_event_name , time_pt , points , interval , averaging_time , mode )
                
        #         # if add_to_seq: #Legacy Code We can add this in later if we really need
        #         #     self.wg.WGFMU_addSequence( channel , vector_name , self.cf( copies ) ) # add copies copies of the pattern "pulse" to the channel
                
        #         return vector_name
        # else:
        #     vector_names = [ self.cstr( f"ch{self.wgfmus[1]}_{patt_name}_{timestamp}" ), self.cstr( f"ch{self.wgfmus[0]}_{patt_name}_{timestamp}" )]
        #     for ch_ind, channel in enumerate(self.wgfmus):
        #         vector_name = vector_names[ch_ind]

        #         # Create pattern for this channel
        #         self.wg.WGFMU_createPattern(vector_name, self.cf(0))

        #         # Select waveform data based on channel index
        #         if ch_ind == 0:  # First channel (VSS)
        #             drive_times = VSS_waveform[0]
        #             drive_voltages = VSS_waveform[1]
        #         elif ch_ind == 1:  # Second channel (VDD)
        #             drive_times = VDD_waveform[0]
        #             drive_voltages = VDD_waveform[1]
        #         else:
        #             print(f"⚠️ Unexpected channel index {ch_ind}, skipping...")
        #             continue  # Skip unexpected channels

        #         # Apply waveform data to the current channel
        #         for time_idx in range(len(drive_times)):
        #             time_pt = self.cf(drive_times[time_idx])
        #             voltage = self.cf(drive_voltages[time_idx])

        #             self.wg.WGFMU_setVector(vector_name, time_pt, voltage)

                
        #         # Add ranging events if they were included
        #         if (len(comp_data) > 0):
        #             ranging_times = comp_data[0]
        #             ranging_settings = comp_data[1]
                    
        #             for ind in range(len(ranging_times)):
        #                 range_time = self.cf(ranging_times[ind] )
        #                 range_setting =  ranging_settings[ind] 
        #                 range_event_name = self.cstr( f"ch{channel}_range{ind}_{timestamp}")
                        
        #                 self.wg.WGFMU_setRangeEvent(vector_name, range_event_name, range_time , range_setting) #as soon as the measurement is done, change the current range we can drive enough current
                        

                
        #         # Add measurement events if they're included
        #         if len( meas_data ) > 0 :
        #             meas_times = meas_data[0]
        #             meas_pts = meas_data[1]
        #             meas_intervals = meas_data[2]
        #             meas_averaging_times = meas_data[3]
        #             meas_modes = meas_data[4]
                    
        #             for ind in range(len( meas_times ) ):
        #                 time_pt = self.cf( meas_times[ind] )
        #                 points = int( meas_pts[ind] )
        #                 interval = self.cf( meas_intervals[ind] )
        #                 averaging_time = self.cf( meas_averaging_times[ind] )
        #                 mode = int( meas_modes[ind] )
        #                 meas_event_name = self.cstr( f"ch{channel}_meas{ind}_{timestamp}" )
                        
        #                 #print( f"{vector_name.value}  {meas_event_name.value}  {time_pt}  {points}  {interval}  {averaging_time}  {mode}")
        #                 self.wg.WGFMU_setMeasureEvent( vector_name , meas_event_name , time_pt , points , interval , averaging_time , mode )
                
        #         # if add_to_seq: #Legacy Code We can add this in later if we really need
        #         #     self.wg.WGFMU_addSequence( channel , vector_name , self.cf( copies ) ) # add copies copies of the pattern "pulse" to the channel
                
        #         return vector_name