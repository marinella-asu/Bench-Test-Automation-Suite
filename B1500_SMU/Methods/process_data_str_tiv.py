import numpy as np
def process_data_str_tiv( self , data_str ):
        """Processes data string and returns values as a tuple of numpy arrays
        Return order is time , voltage , current
        Assumes that measurement includes time AND voltage and current"""
        # remove termination characters
        data_str = data_str.rstrip()
        data_arr = data_str.split( "," )
        
        total_len = len( data_arr )
        vector_len = int( total_len / 3 )
        
        data = np.zeros( total_len ) # format will be time, current, voltage
        
        for ind, el in enumerate(data_arr):
            code = el[0:3] # 3 character data code
            val = float( el[3:] ) # actual data
            data[ind] = val
            
        data = np.reshape( data , (vector_len , 3) )
        
        # data columns
        # col 0: time
        # col 1: current
        # col 2: voltage
        times = data[:,0]
        currents = data[:,1]
        voltages = data[:,2]
        
        return times , voltages , currents