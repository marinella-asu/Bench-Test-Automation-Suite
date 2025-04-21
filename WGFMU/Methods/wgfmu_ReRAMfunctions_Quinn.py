# -*- coding: utf-8 -*-
"""
Created on Thu Apr  4 15:43:28 2024

@author: tnguy290
"""
import b1500_core
import swm_core
import wgfmu_core
import wgfmu_consts as wgc
from wgfmu_core import cstr
import statistics as st

import test_info

import numpy as np
import time
import datetime
import os

import matplotlib.pyplot as plt


b1500 = test_info.b1500
#swm = swm_core.B2200( b2200_gpib_address , DEBUG_PRINT=True )
wgfmu = test_info.wgfmu

ch_vdd = 201 ### WGFMU1
ch_vss = 202 ### WGFMU2
DEBUG_PRINT=test_info.DEBUG_PRINT


#%%useful WGFMU current constants
wgfmu_1ua   = wgc.WGFMU_MEASURE_CURRENT_RANGE_1UA
wgfmu_10ua  = wgc.WGFMU_MEASURE_CURRENT_RANGE_10UA
wgfmu_100ua = wgc.WGFMU_MEASURE_CURRENT_RANGE_100UA
wgfmu_1ma   = wgc.WGFMU_MEASURE_CURRENT_RANGE_1MA
wgfmu_10ma  = wgc.WGFMU_MEASURE_CURRENT_RANGE_10MA


#%% WGFMU functions

def rd_pulses_1terminal( num_reads=1,
              ch_vdd = 201,
              ch_vss = 202,
              t_start=598.9e-6,
              t_settle=1e-6,
              t_read=100e-6,
              rd_period=1e-3,
              meas_pts=1,
              meas_interval=-1,
              meas_averaging=-1,
              t_rise=100e-9,
              v_rd=0.1,
              v_off=0.0,
              range_rd=wgc.WGFMU_MEASURE_CURRENT_RANGE_100UA,
              offset_times=False,
              wgfmu_open_first=True,
              wgfmu_close_after=True,
              VREF=0):
    
    # t_start: time when pulse begins
    # t_settle: time to hold at v_rd before beginning read
    # t_read: time to hold at v_rd for actual read
    # t_rise: voltage rise and fall time
    t0 = t_start          # start at v=0
    t1 = t_start + t_rise # rise to v_rd
    t2 = t1 + t_settle    # wait for voltage to settle
    t3 = t2 + t_read      # hold during read
    t4 = t3 + t_rise      # fall back to 0V
    t5 = rd_period        # end of pattern
    t1_5 = st.mean([t1,t2])
    t2_5 = st.mean([t2,t3])
    #print(f"t1 {t1} t2 {t2} t3 {t3} t4 {t4} t5 {t5}")
    # mean = t2_5       # Mean of the Gaussian function
    # sigma_value = (t3-t2)/10  # Different standard deviations
    # n_points = 100  # Number of points
    # # Gaussian time
    # t = np.random.normal(mean, sigma_value, n_points)
    # ranging_matrix = np.full_like(t, range_rd)
    if t5 < t4:
        raise ValueError("rd_period too short")
    
    # clear existing pattern data
    wgfmu.wg.WGFMU_clear()
        
    
    # Set up main waveform
    if rd_period > 0: # read period will be longer than minimum
        vdd_waveform = [[ 0  ,  v_off    ],
                        [ t0 ,  v_off ], # begin rise
                        [ t1 ,  v_rd ], # reach t_rd, hold until t2
                        [ t1_5, v_rd ],
                        [ t2 ,  v_rd ], # begin read event
                        [ t2_5, v_rd ],
                        [ t3 ,  v_rd ], # end of read pulse, begin fall time
                        [ t4 ,  v_off  ], # fall time done
                        [ t5 ,  v_off  ]] # end of read period
        vss_waveform = [[ 0  ,  v_off  ],
                        [ t5 ,  v_off  ]]
        
        # set up current ranges
        ranging_data = ( 
                         [ 0     ], # times
                         [ range_rd ]  # range settings
                       )
        # ranging_data = ( [0, t ], [ range_rd, ranging_matrix ] )
    else: # end pattern the moment fall time is done
        vdd_waveform = [[ 0  ,  v_off    ],
                        [ t0 ,  v_off ], # begin rise
                        [ t1 ,  v_rd ], # reach t_rd, hold until t2
                        [ t2 ,  v_rd ], # begin read event
                        [ t3 ,  v_rd ], # end of read pulse, begin fall time
                        [ t4 ,  v_off  ]] # fall time done

        
        # set up current ranges
        ranging_data = ( 
                         [ t3     ], # times
                         [ range_rd ]  # range settings
                       )
    
    if meas_interval < 0:
        meas_interval = t_read/meas_pts
    if meas_averaging < 0:
        meas_averaging = t_read/(meas_pts)
    
    # set up measurement events
    measure_mode = wgc.WGFMU_MEASURE_EVENT_DATA_AVERAGED
    #measure_mode = wgc.WGFMU_MEASURE_EVENT_DATA_RAW
    meas_times = [ t1_5 ]
    meas_pts   = [ meas_pts  ]
    meas_interval =  [ meas_interval ]
    meas_averaging = [ meas_averaging ]
    meas_mode = [ measure_mode ]
    meas_data = ( meas_times , meas_pts , meas_interval , meas_averaging , meas_mode )
    
    # convert waveforms to appropriate format
    vdd_waveform = np.array( vdd_waveform )
    vdd_times    = vdd_waveform[:,0]
    vdd_voltages = vdd_waveform[:,1]
    vdd_drive_data = ( vdd_times , vdd_voltages )
    
    vss_waveform = np.array( vss_waveform )
    vss_times    = vss_waveform[:,0]
    vss_voltages = vss_waveform[:,1]
    vss_drive_data = ( vss_times , vss_voltages )
    
    # Create waveform on WGFMU
    wgfmu.create_waveform( ch_vdd , vdd_drive_data , ranging_data=ranging_data , meas_data=meas_data , num_copies=num_reads )
    wgfmu.create_waveform( ch_vss , vss_drive_data , ranging_data=ranging_data , meas_data=meas_data , num_copies=num_reads )
    
    # Run pattern
    t_run = time.perf_counter()
    wgfmu.wgfmu_run( [ch_vdd,ch_vss], open_first=wgfmu_open_first, close_after=wgfmu_close_after )
    
    # Read out data
    times1, vals1 = wgfmu.read_results( ch_vdd )
    
    # Close down WGFMU Session
    times = times1
    currents = vals1
    conductances = currents / (v_rd-VREF)
    
    if offset_times:
        times += t_run
    
    return ( times , currents , conductances)

def prg_2terminal( ch_vdd , ch_vss ,v_prg =2 , v_prg_max=7 , vstep=0 , v_rd=0.1 , t_prg=100e-9 , trise=100e-9 , tsettle=10e-6 , trd=100e-6 , gmin=0e-6 , gmax=0e-6 , pulses_per_voltage=10 , num_pgms=1 , ranging_rd=wgfmu_1ua , range_pgm_set=wgfmu_1ua , range_pgm_rst=wgfmu_1ua , wgfmu_open_first=True, wgfmu_close_after=False ):
    done = False
    g_cur = 0.0
    v_prg_set = v_prg
    v_prg_rst = -v_prg
    
    currents = 0
    times = 0
    pulse_num = 0
    ##### read timings
    tstart = 58.9e-6 #598.9e-6
    t1 = tstart + trise
    t2 = t1 + tsettle
    t3 = t2 + trd
    t4 = t3 + trise
    t2_5 = st.mean([t2,t3])
    ##### prog timings
    t_prg_init = t4 + 100e-6
    t_prg_start = t_prg_init + trise
    t_prg_stop = t_prg_start + t_prg
    t_prg_zero = t_prg_stop + 10e-6
    ##### second read
    t5 = t_prg_zero + tstart
    t6 = t5 + trise
    t7 = t6 + tsettle
    t8 = t7 + trd
    t9 = t8 + trise
    t7_5 = st.mean([t7,t8])
    t_end = t8+30e-6 #t8+300e-6 #NOTE: the wait time is supposed 3-5 times longer than the applied pulse
    
    t_ranging1 = t4 + 10e-6
    t_ranging2 = t_prg_zero + 10e-6
    #################### check conductance state
    # results = rd_pulses_1terminal()
    results = rd_pulses( ch_vss, ch_vdd, num_reads=5, v_rd=v_rd)
    #print(f'{results[2]}')
    g_cur = sum(results[2])/len(results[2])
    #print(f"conductance {sum(results[2])/len(results[2])} and {g_cur}")
    #g_cur = st.mean([results[1][2], results[2][2], results[3][2], results[4][2]])
    if DEBUG_PRINT:
        print( f"..Init Level Read: {g_cur*1e6:.4g} uS [{gmin*1e6:.4g} uS, {gmax*1e6:.4g} uS] ")
    ##############################################
    
    if (g_cur >= gmin) and (g_cur <= gmax):
        done = True
    
        
    while done==False and v_prg < v_prg_max:
        # try:
        #     g_cur = float(g_cur)
        # except ValueError:
        #     print("Variable g_cur is not a numberical type")
        
        set_done = ( g_cur >= gmin )
        rst_done = ( g_cur <= gmax )
        done = np.all(set_done & rst_done)
        #print(f"value of conductance {g_cur}, SET {set_done}, RESET {rst_done}, and DONE {done}")
        if set_done==False:
            print("conductance lower than target, setting now")
            v_prg_set = v_prg_set + vstep
            v_prg = v_prg_set
            ranging_pgm = range_pgm_set
            operation = "SET"
        elif rst_done==False:
            print("conductance higher than target, resetting now")
            v_prg_rst = v_prg_rst - vstep
            v_prg = v_prg_rst
            ranging_pgm = range_pgm_rst
            operation = "RESET"
        print(f"program bias {v_prg:.2g}")    
        
            #print( f"read {v_rd} and prg {v_prg}")
    
        vdd_waveform = [[ 0   , 0     ],
                        [ tstart , 0  ], # begin the pulse
                        [ t1 , v_rd   ], # rising pulse for read
                        [ t2 , v_rd   ], # stabilize read
                        [ t2_5, v_rd  ], # secondary boundary for stabilization and where read operation starts
                        [ t3 , v_rd   ], # end of read
                        [ t4 , 0      ], # falling pulse for read
                        [ t_prg_init  , 0.0  ], # begin pgm rise
                        [ t_prg_start , v_prg  ], # reach v_prg
                        [ t_prg_stop  , v_prg  ], # end vpgm, begin fall
                        [ t_prg_zero  , 0.0    ], # return to 0
                        [ t5   , 0.0   ], # begin read 2
                        [ t6 , v_rd    ], # hold v_rd for 1us for stability
                        [ t7  , v_rd   ], # rd_start
                        [ t7_5, v_rd   ],
                        [ t8  , v_rd   ], # rd_end, begin fall
                        [ t9  , 0.0    ], # return to 0
                        [ t_end, 0.0   ]] # end pattern
        vss_waveform = [[ 0   , 0      ],
                        [ t_end, 0.0    ]      ]
        ranging_data = ( 
                         [ tstart     , t_ranging1  , t_ranging2 ], # times
                         [ ranging_rd , ranging_pgm , ranging_rd ]  # range settings
                         )
        
        # For opposed pulsing, rather than putting a NEGATIVE voltage on the positive electrode
        # we put a POSITIVE voltage on the negative electrode
        # if opposed and (v_pgm < 0 ):
        #     v_pos = 0.0
        #     v_neg = float( np.abs( v_pgm ) )

        
        # vss_waveform = [[ 0        , 0      ],
        #                 [ 398.9e-6 , 0      ], # begin read rise
        #                 [ 399.0e-6 , 0      ], # hold v_rd for 1us for stability 
        #                 [ 400.0e-6 , 0      ], # read start, hold at v_rd
        #                 [ 401.0e-6 , 0      ], # read finish, begin fall
        #                 [ 401.1e-6 , 0.0    ], # return to 0
        #                 [ t_pgm_init  , 0.0  ], # begin pgm rise
        #                 [ t_pgm_start , v_neg  ], # reach v_pgm
        #                 [ t_pgm_stop  , v_neg  ], # end vpgm, begin fall
        #                 [ t_pgm_zero  , 0.0    ], # return to 0
        #                 [ t_rd_init   , 0.0    ], # begin read rise
        #                 [ t_rd_arrive , 0.0    ], # hold v_rd for 1us for stability
        #                 [ t_rd_start  , 0.0    ], # rd_start
        #                 [ t_rd_stop   , 0.0    ], # rd_end, begin fall
        #                 [ t_rd_zero   , 0.0    ], # return to 0
        #                 [ pat_end     , 0.0    ]] # end pattern
        
        # set up current ranges
        # decide based on vpgm whether to use SET or RST current limit

        
        measure_mode = wgc.WGFMU_MEASURE_EVENT_DATA_AVERAGED
        meas_times = [t2_5 , t7_5]
        meas_pts   = [ 1 , 1 ]
        meas_interval =  [ trd , trd ]
        meas_averaging = [ trd/2 , trd/2 ]
        meas_mode = [ measure_mode , measure_mode ]
        meas_data = ( meas_times , meas_pts , meas_interval , meas_averaging , meas_mode )
        
        # convert waveforms to appropriate format
        #print(vdd_waveform)
        vdd_waveform = np.array( vdd_waveform )
        vdd_times    = vdd_waveform[:,0]
        vdd_voltages = vdd_waveform[:,1]
        vdd_drive_data = ( vdd_times , vdd_voltages )
        
        vss_waveform = np.array( vss_waveform )
        vss_times    = vss_waveform[:,0]
        vss_voltages = vss_waveform[:,1]
        vss_drive_data = ( vss_times , vss_voltages )
        
        
        # clear existing pattern data
        wgfmu.wg.WGFMU_clear()
        
        # Create waveform on WGFMU
        wgfmu.create_waveform( ch_vdd , vdd_drive_data , ranging_data=ranging_data , meas_data=meas_data , num_copies=num_pgms )
        wgfmu.create_waveform( ch_vss , vss_drive_data , ranging_data=ranging_data , meas_data=meas_data , num_copies=num_pgms )
        
        wgfmu.wgfmu_run( [ ch_vdd , ch_vss ], open_first=wgfmu_open_first, close_after=wgfmu_close_after )
        
        ###################### SHALL IT BETTER TO USE A SEPERATE READ FUNCTION INSTEAD OF COMBINED READ WITHIN THE PROGRAM ONE?
        # Read out data
        times1, vals1 = wgfmu.read_results( ch_vdd )
        times2, vals2 = wgfmu.read_results( ch_vss )
        
        # Close down WGFMU Session
        times = times1
        currents = vals1
        print(f"currents {vals1}")
        conductances = currents / v_rd
        print(f'\n conductance {conductances} \n')
        g_cur = conductances[-1]
        current = currents[-1]
        #print(f"end of a loop: {g_cur}")
        if DEBUG_PRINT:
            print( f"{operation}   {v_prg:.4g} V \t {g_cur*1e6:.4g} uS \t [{gmin*1e6:.4g} uS,{gmax*1e6:.4g}] uS {done} \t  ({current*1e6:.3g} uA)" )
            
        
        pulse_num += 1
        if (pulse_num<pulses_per_voltage):
            vstep = 0
        else:
            vstep = 0.1
            pulse_num = 0
        # level_num = np.floor( pulse_num / pulses_per_voltage )
        # vstep = level_num*vstep
        
        # pulse_num += 1
        # level_num = np.floor( pulse_num / pulses_per_voltage )
        # v_pgm = v_start + v_inc*level_num
    
        # if offset_times:
        #     t_offset = t_run
        #     times += t_offset
        # else:
        #     t_offset = 0
    
        if (v_prg>v_prg_max):
            print("The device is unprogrammable - Bias Condition Is Over {v_prg_max} V")
        elif (done):
            #print( f"The program operation succeeds with conductance of {g_cur*1e6:.4g} uS \t at bias condition {v_prg:.4g} V \t ({currents*1e6:.3g} uA)")
            print( f"The program operation succeeds with conductance of {g_cur*1e6:.4g} uS \t at bias condition {v_prg:.4g} V \t  ({current*1e6:.3g} uA)")
        
    return ( times , currents , g_cur )

def rd_pulses( ch_vdd, ch_vss, num_reads=1,
              t_start=598.9e-6,
              t_settle=1e-6,
              t_read=100e-6,
              rd_period=1e-3,
              meas_pts=1,
              meas_interval=-1,
              meas_averaging=-1,
              t_rise=100e-9,
              v_rd=0.08,
              v_off=0.0,
              range_rd=wgc.WGFMU_MEASURE_CURRENT_RANGE_100UA,
              offset_times=False,
              wgfmu_open_first=True,
              wgfmu_close_after=True,
              VREF=0):
    
    # t_start: time when pulse begins
    # t_settle: time to hold at v_rd before beginning read
    # t_read: time to hold at v_rd for actual read
    # t_rise: voltage rise and fall time
    t0 = t_start          # start at v=0
    t1 = t_start + t_rise # rise to v_rd
    t2 = t1 + t_settle    # wait for voltage to settle
    t3 = t2 + t_read      # hold during read
    t4 = t3 + t_rise      # fall back to 0V
    t5 = rd_period        # end of pattern
    
    if t5 < t4:
        raise ValueError("rd_period too short")
    
    # clear existing pattern data
    wgfmu.wg.WGFMU_clear()
        
    
    # Set up main waveform
    if rd_period > 0: # read period will be longer than minimum
        vdd_waveform = [[ 0  ,  v_off    ],
                        [ t0 ,  v_off ], # begin rise
                        [ t1 ,  v_rd ], # reach t_rd, hold until t2
                        [ t2 ,  v_rd ], # begin read event
                        [ t3 ,  v_rd ], # end of read pulse, begin fall time
                        [ t4 ,  v_off  ], # fall time done
                        [ t5 ,  v_off  ]] # end of read period
        
        vss_waveform = [[ 0  ,  v_off  ],
                        [ t5 ,  v_off  ]] # hold vss at 0v the entire time
        
        # set up current ranges
        ranging_data = ( 
                         [ 0.00     ], # times
                         [ range_rd ]  # range settings
                       )
    else: # end pattern the moment fall time is done
        vdd_waveform = [[ 0  ,  v_off    ],
                        [ t0 ,  v_off ], # begin rise
                        [ t1 ,  v_rd ], # reach t_rd, hold until t2
                        [ t2 ,  v_rd ], # begin read event
                        [ t3 ,  v_rd ], # end of read pulse, begin fall time
                        [ t4 ,  v_off  ]] # fall time done
        
        vss_waveform = [[ 0  ,  v_off  ],
                        [ t4 ,  v_off  ]] # hold vss at 0v the entire time
        
        # set up current ranges
        ranging_data = ( 
                         [ 0.00     ], # times
                         [ range_rd ]  # range settings
                       )
    
    if meas_interval < 0:
        meas_interval = t_read/meas_pts
    if meas_averaging < 0:
        meas_averaging = t_read/meas_pts
    
    # set up measurement events
    measure_mode = wgc.WGFMU_MEASURE_EVENT_DATA_AVERAGED
    #measure_mode = wgc.WGFMU_MEASURE_EVENT_DATA_RAW
    meas_times = [ t2 ]
    meas_pts   = [ meas_pts  ]
    meas_interval =  [ meas_interval ]
    meas_averaging = [ meas_averaging ]
    meas_mode = [ measure_mode ]
    meas_data = ( meas_times , meas_pts , meas_interval , meas_averaging , meas_mode )
    
    # convert waveforms to appropriate format
    vdd_waveform = np.array( vdd_waveform )
    vdd_times    = vdd_waveform[:,0]
    vdd_voltages = vdd_waveform[:,1]
    vdd_drive_data = ( vdd_times , vdd_voltages )
    
    vss_waveform = np.array( vss_waveform )
    vss_times    = vss_waveform[:,0]
    vss_voltages = vss_waveform[:,1]
    vss_drive_data = ( vss_times , vss_voltages )
    
    # Create waveform on WGFMU
    wgfmu.create_waveform( ch_vdd , vdd_drive_data , ranging_data=ranging_data , meas_data=meas_data , num_copies=num_reads )
    wgfmu.create_waveform( ch_vss , vss_drive_data , ranging_data=ranging_data , meas_data=meas_data , num_copies=num_reads )
    
    # Run pattern
    t_run = time.perf_counter()
    wgfmu.wgfmu_run( [ ch_vdd , ch_vss ], open_first=wgfmu_open_first, close_after=wgfmu_close_after )
    
    # Read out data
    times1, vals1 = wgfmu.read_results( ch_vdd )
    times2, vals2 = wgfmu.read_results( ch_vss )
    
    # Close down WGFMU Session
    times = times1
    currents = vals1
    conductances = currents / (v_rd-VREF)
    
    if offset_times:
        times += t_run
    
    return ( times , currents , conductances , t_run)
    