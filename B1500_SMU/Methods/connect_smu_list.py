def connect_smu_list( self , smu_num_list ):
        # if someone passes just a single channel, turn it into a list for parsing
        if type( smu_num_list ) == int:
            smu_num_list = [ smu_num_list ]
            # yes this is kind of dumb, but whatever
            
        smu_arr = [ str(self.smus[ smu_num - 1 ]) for smu_num in smu_num_list ]
        smu_str = ",".join( smu_arr )
        conn_str = f"CN {smu_str}"
        
        self.b1500.write( conn_str )
        
        return conn_str