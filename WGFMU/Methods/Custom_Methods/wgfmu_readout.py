from B1500.B1500Unified import B1500
import numpy as np
import matplotlib.pyplot as plt
import datetime
import sys
import time

'''
This file will run a readout of the WGFMU 
at all the different current ranges for 3 secs
then save the results to a CSV file.
'''

def wgfmu_readout(self,
                  b1500=None,
                  param_name=None,
                  num_reads=10,
                  v_rd=0.1,
                  read_waveform = None,
                  **overrides):
    try:
        now = datetime.datetime.now()
        date_time = now.strftime("%Y-%m-%d_%H-%M-%S")
    
        final_params = {
            "num_reads": num_reads,
            "v_rd": v_rd,
            "read_waveform": read_waveform,
        }
    
        if b1500 and param_name:
            param_block = dict(b1500.parameters.get(param_name, {}))
            param_block.update(overrides)
            for key, value in param_block.items():
                setattr(b1500, f"{key}_{param_name}", value)
            final_params.update(param_block)
    
        if not b1500 or not param_name:
            final_params.update(overrides)
    
        # Unpack
        num_reads = final_params["num_reads"]
        v_rd = final_params["v_rd"]
        read_waveform = final_params["read_waveform"]
        
        self.wg.WGFMU_clear()
        
        all_curr = [] 
        i = 0

        wgfmu_ranges = {
            "1uA"     : self.wgc.WGFMU_MEASURE_CURRENT_RANGE_1UA,
            "10uA"    : self.wgc.WGFMU_MEASURE_CURRENT_RANGE_10UA,
            "100uA"   : self.wgc.WGFMU_MEASURE_CURRENT_RANGE_100UA,
            "1mA"     : self.wgc.WGFMU_MEASURE_CURRENT_RANGE_1MA
        }
        
        for range in wgfmu_ranges:
            
            results2 = self.rd_pulses_1terminal(
                    b1500, ch_vdd=b1500.test_info.ch_vdd, ch_vss=b1500.test_info.ch_vss,
                    num_reads=1, t_start=1e-6, t_settle=3e-6, t_read=10e-3,
                    rd_period=100e-3, meas_pts=3001, meas_interval=1e-3, meas_averaging=-1,
                    t_rise=100e-9, v_rd=v_rd, v_off=0.0,
                    range_rd=range[0], ##Change to different ranges as needed
                    offset_times=False, wgfmu_open_first=True, wgfmu_close_after=True, alternate_waveform = read_waveform)

            times, currents, conductances = results2
            currents = currents[:-1]
            times = times[:-1]

            plt.figure()
            plt.plot(times, currents)
            plt.xlabel("Time (s)")
            plt.ylabel("Current (A)")
            plt.title(f"WGFMU Noise Readout: {range} Range")
            plt.grid(True)
            plt.show()
            plt.close()
            
            if i == 0:
                base_times = times  # Save time once
                i = i + 1
            all_curr.append(currents)

        #Clear and close WGFMU connection
        b1500.connection.write("CL")
        b1500.wgfmu.wg.WGFMU_clear()
        
        final_array_rtn= np.column_stack([base_times] + all_curr)

        headers = ["Time (s)"] + [f"Noise Readout {range}" for range in wgfmu_ranges]
        b1500.save_numpy_to_csv(b1500, final_array_rtn, filename=f"WGFMUReadout", headers = headers)

    except KeyboardInterrupt as e:
        #Clear and close WGFMU connection
        b1500.connection.write("CL")
        b1500.wgfmu.wg.WGFMU_clear()
        if i > 0:
            final_array_rtn= np.column_stack([base_times] + all_curr)
            
            headers = ["Time (s)"] + [f"Noise Readout {range}" for range in wgfmu_ranges]
            b1500.save_numpy_to_csv(b1500, final_array_rtn, filename="WGFMUReadout", headers = headers)