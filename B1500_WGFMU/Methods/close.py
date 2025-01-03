def close(self, channel_list=[]):
        # Reset and close down WGFMU connection
        if len(channel_list) == 0:
            self.wg.WGFMU_initialize() # WGFMU_DISCONNECT( 101 )
        else:
            for channel in channel_list:
                self.wg.WGFMU_disconnect(channel)
                
        self.wg.WGFMU_closeSession()