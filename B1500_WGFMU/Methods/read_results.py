def read_results( self , channel_id ):
        measured_size = ct.c_int()
        total_size = ct.c_int()
        
        # Pass references to our size variables into this function so they can be updated
        self.wg.WGFMU_getMeasureValueSize( channel_id, ct.byref( measured_size ), ct.byref( total_size ) )
        
        #print(measured_size.value)
        # print(f"THIS IS ERROR {measured_size}")
        times = np.zeros( measured_size.value )
        values = np.zeros( measured_size.value )
        
        for ind in range( 0, measured_size.value ):
            time = ct.c_double()
            value = ct.c_double()
            #voltage = ct.c_double()
            
            self.wg.WGFMU_getMeasureValue( channel_id , ind , ct.byref( time ) , ct.byref( value ) )
            #wg.WGFMU_getInterpolatedForceValue( channel_id1 , time , ct.byref( voltage ) )
            #print(f"This is channel_id: {channel_id}") #Quinn
            #print(f"This is time: {time}") #Quinn
            #print(f"This is value: {value}") #Quinn
            times[ind] = time.value
            values[ind] = value.value
            
        #print("This is matrix of time:", time) #Quinn
        #print("This is matrix of value:", value) #Quinn
        
        
        return times, values