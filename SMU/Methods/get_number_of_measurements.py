def get_number_of_measurements(self):
    """
    Queries the B1500 for the number of measurement data items in the output buffer.

    Returns:
    - result (int): Number of stored measurements
    """
    result = self.b1500.query("NUB?")  # Query the number of measurements in buffer
    result = result.strip()  # Remove any extra whitespace or termination characters
    result = int(result)  # Convert response to an integer
    
    return result
