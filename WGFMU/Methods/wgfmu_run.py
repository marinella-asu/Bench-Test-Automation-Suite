import ctypes as ct  # Import C types for low-level hardware interaction
import time  # Import time module for delays
import wgfmu_consts as wgc  # Import constants for WGFMU operations

def wgfmu_run( self , channel_list , open_first=True, close_after=False ):
        # Activate WGFMU
        if open_first:
            self.wg.WGFMU_openSession( self.wgfmu_gpib_str )
            self.wg.WGFMU_initialize()
        
        # Set up channels
        for channel in channel_list:
            # Set up current read mode on WGFMU1/2
            self.wg.WGFMU_setOperationMode( channel , wgc.WGFMU_OPERATION_MODE_FASTIV )
            self.wg.WGFMU_setMeasureMode( channel , wgc.WGFMU_MEASURE_MODE_CURRENT )
        
        # Connect to channels
        for channel in channel_list:
            self.wg.WGFMU_connect( channel )
        
        # Execute the patterns
        t_init = time.perf_counter()
        
        self.wg.WGFMU_execute()
        self.wg.WGFMU_waitUntilCompleted()
        
        t_final = time.perf_counter()
        
        #t_tot = t_final - t_init
        #print( f"WGFMU TIME: {t_tot:.3g}" )
        
        if close_after:
            for channel in channel_list:
                self.wg.WGFMU_disconnect(channel)
            self.wg.WGFMU_closeSession()
            #self.close()