def create_waveform( self , ch_list , drive_data , ranging_data=() , meas_data=(), num_copies=1 , add_to_sequence=True , pattern_name="" ):
        # drive data: tuple, (time , voltage) , both numpy vectors
        # ranging data: tuple ( time , range setting ) , numpy vector and list
        # meas data: tuple (time , Npts , interval , averaging time , mode )
        
        # if someone sends in just one channel, expand it to a list for the following logic
        if type(ch_list) == int:
            ch_list = [ ch_list ]
            
        timestamp = time.perf_counter()
        vector_names = [ cstr( f"ch{channel}_{pattern_name}_{timestamp}" ) for channel in ch_list ]
        for ch_ind in range(len(ch_list)):
            vector_name = vector_names[ch_ind]
            channel = ch_list[ch_ind]
            #print( f"Creating pattern {vector_name} for channel {channel}...")
            self.wg.WGFMU_createPattern( vector_name , cf(0) )
            
            drive_times = drive_data[0]
            drive_voltages = drive_data[1]
            
            
            for ind in range(len( drive_times ) ):
                time_pt = cf( drive_times[ind] )
                voltage = cf( drive_voltages[ind] )
                #print(f"Vector: {vector_name.value}    T {time_pt.value}    V {voltage.value:.4g}")
                
                self.wg.WGFMU_setVector( vector_name , time_pt , voltage )
            
            # Add ranging events if they were included
            if len( ranging_data ) > 0:
                ranging_times = ranging_data[0]
                ranging_settings = ranging_data[1]
                
                for ind in range(len( ranging_times ) ):
                    range_time = cf( ranging_times[ind] )
                    range_setting =  ranging_settings[ind] 
                    range_event_name = cstr( f"ch{channel}_range{ind}_{timestamp}")
                    
                    self.wg.WGFMU_setRangeEvent( vector_name, range_event_name, range_time , range_setting ) #as soon as the measurement is done, change the current range we can drive enough current
                    

            
            # Add measurement events if they're included
            if len( meas_data ) > 0 :
                meas_times = meas_data[0]
                meas_pts = meas_data[1]
                meas_intervals = meas_data[2]
                meas_averaging_times = meas_data[3]
                meas_modes = meas_data[4]
                #meas_event_names = meas_data[5]
                
                for ind in range(len( meas_times ) ):
                    time_pt = cf( meas_times[ind] )
                    points = int( meas_pts[ind] )
                    interval = cf( meas_intervals[ind] )
                    averaging_time = cf( meas_averaging_times[ind] )
                    mode = int( meas_modes[ind] )
                    meas_event_name = cstr( f"ch{channel}_meas{ind}_{timestamp}" )
                    
                    #print( f"{vector_name.value}  {meas_event_name.value}  {time_pt}  {points}  {interval}  {averaging_time}  {mode}")
                    self.wg.WGFMU_setMeasureEvent( vector_name , meas_event_name , time_pt , points , interval , averaging_time , mode )
            
            if add_to_sequence:
                self.wg.WGFMU_addSequence( channel , vector_name , cf( num_copies ) ) # add num_copies copies of the pattern "pulse" to the channel
            
            return vector_name