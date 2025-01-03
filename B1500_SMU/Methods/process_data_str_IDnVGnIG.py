def process_data_str_IDnVGnIG( self , data_str ):
        """Processes data string and returns values as a tuple of numpy arrays
        Return order is time , voltage , current
        Assumes that measurement includes time AND voltage and current"""
        # remove termination characters
        data_str = data_str.rstrip()
        data_arr = data_str.split( "," )
        
        total_len = len( data_arr )
        vector_len = int( total_len / 5 )
        
        data = np.zeros( total_len ) # format will be time, current, voltage
        
        for ind, el in enumerate(data_arr):
            code = el[0:3] # 3 character data code
            val = float( el[3:] ) # actual data
            data[ind] = val
            
        data = np.reshape( data , (vector_len , 5) )
        
        # data columns
        # col 0: time
        # col 1: current
        # col 2: voltage
        drain_times = data[:,0]
        drain_currents = data[:,1]
        gate_times = data[:,2]
        gate_currents = data[:,3]
        gate_voltages = data[:,4]
        
        return drain_times , drain_currents, gate_times, gate_currents, gate_voltages
    