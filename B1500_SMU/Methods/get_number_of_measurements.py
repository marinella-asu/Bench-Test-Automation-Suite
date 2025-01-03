def get_number_of_measurements(self):
        result = self.b1500.query("NUB?")
        result = result.strip()
        result = int(result)
        
        return result