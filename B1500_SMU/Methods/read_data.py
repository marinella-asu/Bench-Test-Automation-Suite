def read_data( self ):
        """
        Reads data from b1500 and returns time, voltage, and current

        """
        data = self.b1500.read()
        times , voltage , current = self.process_data_str_tiv( data )
        
        return ( times , voltage , current )