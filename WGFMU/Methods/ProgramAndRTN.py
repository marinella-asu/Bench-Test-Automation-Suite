import numpy as np
import matplotlib.pyplot as plt
import datetime
import sys


def ProgramAndRTN(self,
                  b1500=None,
                  param_name=None,
                  min_gtarget=300e-6,
                  max_gtarget=1000e-6,
                  num_level=7,
                  num=30,
                  num_reads=10,
                  v_rd=0.1,
                  v_prg=1.0,
                  v_rst = -1,
                  vstep=0.1,
                  v_prg_max=9.8,
                  v_count=0,
                  v_countmax=40,
                  goffset=1e-6,
                  ProgramTargetOffset = 10e-6,
                  read_waveform = None,
                  program_waveform = None,
                  RTN_waveform = None,
                  **overrides):
    try:
        now = datetime.datetime.now()
        date_time = now.strftime("%Y-%m-%d_%H-%M-%S")
    
        final_params = {
            "min_gtarget": min_gtarget,
            "max_gtarget": max_gtarget,
            "num_level": num_level,
            "num": num,
            "num_reads": num_reads,
            "v_rd": v_rd,
            "v_prg": v_prg,
            "v_rst": v_rst,
            "vstep": vstep,
            "v_prg_max": v_prg_max,
            "v_count": v_count,
            "v_countmax": v_countmax,
            "goffset": goffset,
            "ProgramTargetOffset": ProgramTargetOffset,
            "read_waveform": read_waveform,
            "program_waveform": program_waveform,
            "RTN_waveform": RTN_waveform,
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
        min_gtarget = final_params["min_gtarget"]
        max_gtarget = final_params["max_gtarget"]
        num_level = final_params["num_level"]
        num = final_params["num"]
        num_reads = final_params["num_reads"]
        v_rd = final_params["v_rd"]
        v_prg = final_params["v_prg"]
        v_rst = final_params["v_rst"]
        v_prg_max = final_params["v_prg_max"]
        v_count = final_params["v_count"]
        v_countmax = final_params["v_countmax"]
        goffset = final_params["goffset"]
        ProgramTargetOffset = final_params["ProgramTargetOffset"]
        read_waveform = final_params["read_waveform"]
        program_waveform = final_params["program_waveform"]
        RTN_waveform    = final_params["RTN_waveform"]
        
        self.wg.WGFMU_clear()
        
        all_conductances = []  # To store each conductance column
        
        gtargets = np.linspace(min_gtarget, max_gtarget, num=num_level)
        print("###################################")
        print(f"The target conductances are {gtargets}")
        print("###################################")
        i = 0
        for gtarget in gtargets:
            gmin = gtarget - ProgramTargetOffset #Target Range
            gmax = gtarget + ProgramTargetOffset
            succeed = False
    
            while not succeed and v_count < v_countmax:
                results1 = self.prg_2terminal(
                    b1500, v_prg=v_prg, v_rst = v_rst, v_prg_max=v_prg_max, v_rd=v_rd, vstep = vstep,
                    t_prg=100e-9, ranging_rd=self.get_wgfmu_range_for_gtarget(gtarget),
                    gmin=gmin, gmax=gmax, pulses_per_voltage=num, read_waveform = read_waveform, program_waveform = program_waveform)
    
                self.wg.WGFMU_setForceDelay(b1500.test_info.ch_vdd, 100)
                self.wg.WGFMU_setForceDelay(b1500.test_info.ch_vss, 100)
                self.wg.WGFMU_clear()
                self.wg.WGFMU_closeSession()
    
                results = self.rd_pulses_1terminal(
                    b1500, ch_vdd=b1500.test_info.ch_vdd, ch_vss=b1500.test_info.ch_vss,
                    num_reads=num_reads, t_start=1e-6, t_settle=3e-6, t_read=10e-3,
                    rd_period=100e-3, meas_pts=1, meas_interval=1e-4, meas_averaging=-1,
                    t_rise=100e-9, v_rd=v_rd, v_off=0.0,
                    range_rd=self.get_wgfmu_range_for_gtarget(gtarget),
                    offset_times=False, wgfmu_open_first=True, wgfmu_close_after=True, alternate_waveform = read_waveform)
    
                everything = results[2]
                all_except_first = everything[1:]
                # print(all_except_first)
                g_d = sum(all_except_first) / len(all_except_first)
    
                gmin1 = gmin - goffset
                gmax1 = gmax + goffset
                succeed = (g_d >= gmin1) and (g_d <= gmax1)
    
                print(f"The state: {succeed} with conductance: {g_d} in range {gmin1} to {gmax1}")
    
                if v_count >= v_countmax - 1:
                    print(f"Unable to reach target {gtarget} due to max programming attempts")
                    return False
    
                v_count += 1
                print(f"PROGRAM STATUS: {succeed}, attempt {v_count}/{v_countmax}")
    
            if succeed:
                print("SUCCESS")
                v_count = 1
                
            
            # Long-term RTN Read
            results2 = self.rd_pulses_1terminal(
                b1500, ch_vdd=b1500.test_info.ch_vdd, ch_vss=b1500.test_info.ch_vss,
                num_reads=1, t_start=1e-6, t_settle=3e-6, t_read=10e-3,
                rd_period=100e-3, meas_pts=3001, meas_interval=1e-3, meas_averaging=-1,
                t_rise=100e-9, v_rd=v_rd, v_off=0.0,
                range_rd=self.get_wgfmu_range_for_gtarget(gtarget),
                offset_times=False, wgfmu_open_first=True, wgfmu_close_after=True, alternate_waveform = RTN_waveform)
    
            times, currents, conductances = results2
            conductances = conductances[:-1]
            times = times[:-1]
            # print(times)
            # print("currents")
            # print(currents)
            # print("conductances")
            # print(conductances)
            
            if i == 0:
                base_times = times  # Save time once
                i = i + 1
            all_conductances.append(conductances)
    
            plt.figure()
            plt.plot(times, conductances*1e6)
            plt.xlabel("Time (s)")
            plt.ylabel("Conductance (uS)")
            plt.title(f"RTN Readout for Target {gtarget*1e6:.2f}uS")
            plt.grid(True)
            plt.show()
            plt.close()
            
            
       
        # Stack everything: times as first column, each conductance as additional columns
        final_array = np.column_stack([base_times] + all_conductances)
        
        # Plot all conductance traces
        plt.figure()
        for i, conductance in enumerate(all_conductances):
            plt.plot(base_times, conductance*1e6, label=f"Target {gtargets[i]*1e6:.2f} uS")
        
        plt.xlabel("Time (s)")
        plt.ylabel("Conductance (uS)")
        plt.title(f"RTN Readout for Conductance Targets (uS)")
        plt.grid(True)
        plt.legend()
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        plt.tight_layout()
        plt.show()
        plt.close()
        # Generate headers
        headers = ["Time (s)"] + [f"Conductance_Target_{i+1} (S)" for i in range(len(all_conductances))]

        b1500.save_numpy_to_csv(b1500, final_array, filename="SuccessCompleteProgramRTNOutput", headers = headers)
        return True
    except KeyboardInterrupt as e:
         b1500.connection.write("CL")
         b1500.wgfmu.wg.WGFMU_clear()
         if i > 0:
            final_array = np.column_stack([base_times] + all_conductances)
            # Generate headers
            headers = ["Time (s)"] + [f"Conductance_Target_{i+1} (S)" for i in range(len(all_conductances))]
            b1500.save_numpy_to_csv(b1500, final_array, filename="StoppedProgramRTNOutput", headers = headers)
         print(e)

def get_wgfmu_range_for_gtarget(self, gtarget):
    if gtarget >= 100e-6:
        return self.wgc.WGFMU_MEASURE_CURRENT_RANGE_1MA
    elif gtarget >= 2e-6:
        return self.wgc.WGFMU_MEASURE_CURRENT_RANGE_100UA
    elif gtarget >= 0.1e-6:  
        return self.wgc.WGFMU_MEASURE_CURRENT_RANGE_1UA
    else:
        raise ValueError(f"Target conductance {gtarget} S is too small for reliable WGFMU measurement.")