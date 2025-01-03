def check_err(self, debug_code=""):
        
        self.b1500.write( "ERR?" )
        results = self.b1500.read()
        results = results.strip()
        
        results_print = results.replace(",", "\t")
        print(f"{debug_code}{results_print}")
        
        return results