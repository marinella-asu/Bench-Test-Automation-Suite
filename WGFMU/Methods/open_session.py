def open_session(self):
        self.wg.WGFMU_openSession( self.wgfmu_gpib_str )
        self.wg.WGFMU_initialize()