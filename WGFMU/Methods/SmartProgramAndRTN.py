import numpy as np
import matplotlib.pyplot as plt
import datetime
import sys


def SmartProgramAndRTN(self,
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
                boundary_super_coarse = 100e-6,
                boundary_coarse = 50e-6,
                boundary_fine = 50e-6,
                boundary_ultra_fine = 0.5e-6,
                super_coarse_step = 100e-6,
                coarse_step = 25e-6,
                fine_step = 25e-6,
                ultra_fine_step = 0.5e-6,
                ultra_ultra_fine_step = 0.5e-6,
                use_super_coarse = False,
                use_fine = False,
                use_ultra_fine = False,
                use_ultra_ultra_fine = False,
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
            "boundary_super_coarse": boundary_super_coarse,
            "boundary_coarse": boundary_coarse,
            "boundary_fine": boundary_fine,
            "boundary_ultra_fine": boundary_ultra_fine,
            "super_coarse_step": super_coarse_step,
            "coarse_step": coarse_step,
            "fine_step": fine_step,
            "ultra_fine_step": ultra_fine_step,
            "ultra_ultra_fine_step": ultra_ultra_fine_step,
            "use_super_coarse": use_super_coarse,
            "use_fine": use_fine,
            "use_ultra_fine": use_ultra_fine,
            "use_ultra_ultra_fine": use_ultra_ultra_fine
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
        boundary_super_coarse = final_params["boundary_super_coarse"]
        boundary_coarse = final_params["boundary_coarse"]
        boundary_fine = final_params["boundary_fine"]
        boundary_ultra_fine = final_params["boundary_ultra_fine"]
        super_coarse_step = final_params["super_coarse_step"]
        coarse_step = final_params["coarse_step"]
        fine_step = final_params["fine_step"]
        ultra_fine_step = final_params["ultra_fine_step"]
        ultra_ultra_fine_step = final_params["ultra_ultra_fine_step"]
        use_super_coarse = final_params["use_super_coarse"]
        use_fine = final_params["use_fine"]
        use_ultra_fine = final_params["use_ultra_fine"]
        use_ultra_ultra_fine = final_params["use_ultra_ultra_fine"]


        
        self.wg.WGFMU_clear()
        
        all_conductances = []  # To store each conductance column
        
        # gtargets 
        gtargets = generate_gtargets(max_gtarget, min_gtarget,
                                    boundary_super_coarse, boundary_coarse, boundary_fine, boundary_ultra_fine,
                                    super_coarse_step, coarse_step, fine_step, ultra_fine_step, ultra_ultra_fine_step,
                                    use_super_coarse, use_fine, use_ultra_fine, use_ultra_ultra_fine)
        print("###################################")
        print(f"The target conductances are {gtargets}")
        print("###################################")
        i = 0
        for gtarget in gtargets:
            tolerance = get_tolerance(gtarget)
            gmin = max(gtarget - tolerance, 0)
            gmax = gtarget + tolerance
            succeed = False


            print(f"[{i+1}] gtarget = {gtarget:.2e}, tolerance = ±{tolerance:.1e} → range = [{gmin:.2e}, {gmax:.2e}]")

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
    
                goffset_now = get_goffset(gtarget)
                gmin1 = gmin - goffset_now
                gmax1 = gmax + goffset_now
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

def generate_gtargets(Gmax, Gmin,
                      boundary_super_coarse, boundary_coarse, boundary_fine, boundary_ultra_fine,
                      super_coarse_step, coarse_step, fine_step, ultra_fine_step, ultra_ultra_fine_step,
                      use_super_coarse=True, use_fine=False, use_ultra_fine=False, use_ultra_ultra_fine=False):
    
    gtargets = []
    
    # super-coarse
    if use_super_coarse:
        super_coarse_range = np.arange(Gmax, boundary_super_coarse - super_coarse_step, -super_coarse_step)
        gtargets.extend(np.round(super_coarse_range, 9))
        if boundary_super_coarse not in gtargets:
            gtargets.append(np.round(boundary_super_coarse, 9))
    
    # coarse
    coarse_range = np.arange(boundary_super_coarse - coarse_step, boundary_coarse - coarse_step, -coarse_step)
    gtargets.extend(np.round(coarse_range, 9))
    if boundary_coarse not in gtargets:
        gtargets.append(np.round(boundary_coarse, 9))

    # fine
    if use_fine:
        fine_range = np.arange(boundary_coarse - fine_step, boundary_fine - fine_step, -fine_step)
        gtargets.extend(np.round(fine_range, 9))
        if boundary_fine not in gtargets:
            gtargets.append(np.round(boundary_fine, 9))

    # ultra-fine
    if use_ultra_fine:
        ultra_fine_range = np.arange(boundary_fine - ultra_fine_step, boundary_ultra_fine - ultra_fine_step, -ultra_fine_step)
        gtargets.extend(np.round(ultra_fine_range, 9))
        if boundary_ultra_fine not in gtargets:
            gtargets.append(np.round(boundary_ultra_fine, 9))

    # ultra-ultra-fine
    if use_ultra_ultra_fine:
        ultra_ultra_fine_range = np.arange(boundary_ultra_fine - ultra_ultra_fine_step, Gmin - ultra_ultra_fine_step, -ultra_ultra_fine_step)
        gtargets.extend(np.round(ultra_ultra_fine_range, 9))
        if Gmin not in gtargets:
            gtargets.append(np.round(Gmin, 9))
    
    gtargets = [g for g in gtargets if g >= Gmin]
    gtargets = sorted(np.unique(gtargets), reverse=True)
    
    return np.array(gtargets)

def get_goffset(gtarget):
    if gtarget >= 50e-6:
        return 1e-6
    elif gtarget >= 1e-6:
        return 0.1e-6
    elif gtarget >= 0.1e-6:
        return 0.05e-6
    else:
        return 0.01e-6

    
def get_tolerance(gtarget):
      if gtarget >= 50e-6:
        return 1e-6
      elif gtarget >= 1e-6:
        return 0.4e-6
      else:
        return 10e-9