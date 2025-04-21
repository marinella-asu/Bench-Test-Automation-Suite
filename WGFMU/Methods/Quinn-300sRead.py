import numpy as np
import matplotlib.pyplot as plt
import datetime
import sys


def ProgramAndRTN (self, b1500):
    now = datetime.datetime.now()
    date_time = now.strftime("%Y-%m-%d_%H-%M-%S")

    min_gtarget=300e-6 #Default for GMinimum: Set a G_Minimum parameter if you want this to be different
    if hasattr(b1500.test_info, "G_Minimum_Target"):
        min_gtarget = b1500.test_info.G_Minimum

    max_gtarget=1000e-6 #Default for GMinimum: Set a G_Minimum parameter if you want this to be different
    if hasattr(b1500.test_info, "G_Maximum_Target"):
        max_gtarget = b1500.test_info.G_Minimum
    
    num_level = 7 #Default for GMinimum: Set a G_Minimum parameter if you want this to be different
    if hasattr(b1500.test_info, "G_Maximum_Target"):
        num_level = b1500.test_info.G_Minimum

    num = 30          # Default iterations per program‑voltage level; override with Prog_Num
    if hasattr(b1500.test_info, "Prog_Num"):
        num = b1500.test_info.Prog_Num

    num_reads = 10    # Default reads per verification stage; override with Prog_Num_Reads
    if hasattr(b1500.test_info, "Prog_Num_Reads"):
        num_reads = b1500.test_info.Prog_Num_Reads

    v_rd = 0.1        # Default read voltage; override with V_Read
    if hasattr(b1500.test_info, "V_Read"):
        v_rd = b1500.test_info.V_Read

    v_prg = 1.0       # Starting program voltage; override with V_Prog_Start
    if hasattr(b1500.test_info, "V_Prog_Start"):
        v_prg = b1500.test_info.V_Prog_Start

    vstop = 0.0       # Stop‑voltage threshold (clamp); override with V_Stop
    if hasattr(b1500.test_info, "V_Stop"):
        vstop = b1500.test_info.V_Stop

    v_prg_max = 9.8   # Maximum allowed program voltage; override with V_Prog_Max
    if hasattr(b1500.test_info, "V_Prog_Max"):
        v_prg_max = b1500.test_info.V_Prog_Max

    v_count = 0       # Counter for applied program steps (initialised to 0)
    # No override needed—this will be incremented during the algorithm

    v_countmax = 40   # Maximum program steps permitted; override with V_Count_Max
    if hasattr(b1500.test_info, "V_Count_Max"):
        v_countmax = b1500.test_info.V_Count_Max

    goffset = 1e-6    # Gate‑current offset for compliance; override with G_Offset
    if hasattr(b1500.test_info, "G_Offset"):
        goffset = b1500.test_info.G_Offset


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
                sys.exit(0)

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