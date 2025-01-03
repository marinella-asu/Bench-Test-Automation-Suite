def check_operation_complete(self):
        result = self.b1500.query("*OPC?")
        result = result.strip()
        result = int(result)
        
        return result