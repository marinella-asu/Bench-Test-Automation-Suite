def check_errors( self , ret=-1, step_id=-1 ):
        if( ret != wgc.WGFMU_NO_ERROR ):
            size = ct.c_int(1)
            self.wg.WGFMU_getErrorSize( ct.byref(size) )
            
            if ( size.value > 0 ):
                
                msg = ct.create_string_buffer( size.value + 1 )
                self.wg.WGFMU_getError( ct.byref(msg) , ct.byref(size) )
                if(step_id > 0):
                    msg_str = msg.value.decode('utf-8')
                    print( f"ID {step_id}: " + msg_str)
                else:
                    print( msg.value )
        
        return ret 