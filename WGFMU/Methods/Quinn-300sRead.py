import numpy as np
import matplotlib.pyplot as plt
import datetime
import sys


def ProgramAndRTN (self,
                    b1500=None,
                    param_name=None,
                    # --------- defaults ---------
                    min_gtarget=300e-6,
                    max_gtarget=1000e-6,
                    num_level=7,
                    num=30,
                    num_reads=10,
                    v_rd=0.1,
                    v_prg=1.0,
                    vstop=0.0,
                    v_prg_max=9.8,
                    v_count=0,
                    v_countmax=40,
                    goffset=1e-6,
                    **overrides):
    now = datetime.datetime.now()
    date_time = now.strftime("%Y-%m-%d_%H-%M-%S")

        # 1)  Defaults
    final_params = {
        "min_gtarget": 300e-6,   # ‑‑ G_Minimum_Target
        "max_gtarget": 1000e-6,  # ‑‑ G_Maximum_Target
        "num_level":   7,        # ‑‑ Num_Levels
        "num":         30,       # ‑‑ Prog_Num
        "num_reads":   10,       # ‑‑ Prog_Num_Reads
        "v_rd":        0.1,      # ‑‑ V_Read
        "v_prg":       1.0,      # ‑‑ V_Prog_Start
        "vstop":       0.0,      # ‑‑ V_Stop
        "v_prg_max":   9.8,      # ‑‑ V_Prog_Max
        "v_count":     0,        # (initial counter)
        "v_countmax":  40,       # ‑‑ V_Count_Max
        "goffset":     1e-6      # ‑‑ G_Offset
    }

    # 2)  Load parameter‑block values (if provided)
    if b1500 and param_name:                       # same pattern as before
        param_block = dict(b1500.parameters.get(param_name, {}))
        param_block.update(overrides)              # runtime overrides win

        # expose each setting as   b1500.<key>_<param_name>
        for key, value in param_block.items():
            setattr(b1500, f"{key}_{param_name}", value)

        final_params.update(param_block)           # merge into master dict

    # 3)  If we weren’t given a param block at all, just apply overrides
    if not b1500 or not param_name:
        final_params.update(overrides)

    # 4)  Unpack for easy use downstream
    min_gtarget  = final_params["min_gtarget"]
    max_gtarget  = final_params["max_gtarget"]
    num_level    = final_params["num_level"]
    num          = final_params["num"]
    num_reads    = final_params["num_reads"]
    v_rd         = final_params["v_rd"]
    v_prg        = final_params["v_prg"]
    vstop        = final_params["vstop"]
    v_prg_max    = final_params["v_prg_max"]
    v_count      = final_params["v_count"]
    v_countmax   = final_params["v_countmax"]
    goffset      = final_params["goffset"]



    gtargets=np.linspace(min_gtarget, max_gtarget, num=num_level)
    print("###################################")
    print(f"The target conductances are {gtargets}")
    print("###################################")

    for i, gtarget in enumerate(gtargets):
        gmin = gtarget - 2e-6
        gmax = gtarget + 2e-6
        succeed = False

        while succeed == False and v_count < v_countmax:
            results1 = self.prg_2terminal(self, b1500, self.test_info.ch_vdd, self.test_info.ch_vss, v_prg = v_prg , v_prg_max=v_prg_max , v_rd=v_rd , t_prg=100e-9, ranging_rd=self.wgc.WGFMU_MEASURE_CURRENT_RANGE_100UA, gmin=gmin , gmax=gmax , pulses_per_voltage=num)

            self.wg.WGFMU_setForceDelay (self.test_info.ch_vdd, 100)
            self.wg.WGFMU_setForceDelay (self.test_info.ch_vss, 100)
            self.wg.WGFMU_clear()
            self.wg.WGFMU_closeSession()

            results = self.rd_pulses_1terminal(self, b1500, ch_vdd=self.test_info.ch_vdd, ch_vss=self.test_info.ch_vss, num_reads=num_reads,
                                          t_start=1e-6,
                                          t_settle=3e-6,
                                          t_read=10e-3,
                                          rd_period=100e-3, ##Multiply by the num_reads to get total read time
                                          meas_pts=1,
                                          meas_interval=-1,
                                          meas_averaging=-1,
                                          t_rise=100e-9,
                                          v_rd=v_rd,
                                          v_off=0.0,
                                          range_rd= self.wgc.WGFMU_MEASURE_CURRENT_RANGE_100UA,
                                          offset_times=False,
                                          wgfmu_open_first=True,
                                          wgfmu_close_after=True)

            everything = results[2]
            all_except_first = everything[1:]
            print(f"\n \n conductance range: {all_except_first} \n \n")
            g_d = sum(all_except_first)/len(all_except_first)

            gmin1 = gmin - goffset
            gmax1 = gmax + goffset
            succeed = (g_d >= gmin1) and (g_d <= gmax1)
            print (f" the state: {succeed} with conductance: {g_d} in the range of min {gmin1} and max {gmax1}")
            if v_count >= v_countmax - 1:
                print( f"Unable to set to the target conductance state {gtarget} due to reach the maximum number of program")
                return False

            v_count += 1
            print(f" \n \n \n THE STATUS OF THE PROGRAM OPERATION IS {succeed} and count is {(v_count<v_countmax)} \n \n \n")       
        if succeed == True:
            print(f"results from program{results1}")
            conductance = results1[2]
            print("IT SUCCEEDS")
            
        results2 = self.rd_pulses_1terminal( ch_vdd=self.test_info.ch_vdd, ch_vss=self.test_info.ch_vss, num_reads=3000,
                                        t_start=1e-6,
                                        t_settle=3e-6,
                                        t_read=10e-3,
                                        rd_period=100e-3, ##Multiply by the num_reads to get total read time
                                        meas_pts=1,
                                        meas_interval=-1,
                                        meas_averaging=-1,
                                        t_rise=100e-9,
                                        v_rd=v_rd,
                                        v_off=0.0,
                                        range_rd=self.wgc.WGFMU_MEASURE_CURRENT_RANGE_100UA,
                                        offset_times=False,
                                        wgfmu_open_first=True,
                                        wgfmu_close_after=True)

        times = results2[0]
        currents = results2[1]
        conductances = results2[2]
        
        plt.figure()
        plt.plot(times,conductances)
        plt.show()
        plt.close()
        return True