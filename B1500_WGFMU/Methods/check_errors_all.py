def check_errors_all( self, step_code="", print_errors=True ):
        done = False
        error_list = []
        while not done:
            size = ct.c_int(1)
            self.wg.WGFMU_getErrorSize( ct.byref(size) )
            
            if ( size.value > 0 ):
                
                msg = ct.create_string_buffer( size.value + 1 )
                self.wg.WGFMU_getError( ct.byref(msg) , ct.byref(size) )
                msg_str = msg.value.decode( 'ascii' )
                msg_str = msg_str.replace( "\n" , "\t" )
                error_list.append(msg_str)
                if print_errors:
                    print( f"{step_code}{msg_str}" )
            else:
                done = True
        return error_list