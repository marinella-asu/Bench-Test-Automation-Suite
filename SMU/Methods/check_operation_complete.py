def check_operation_complete(self):
    """
    Queries the B1500 to check if the current operation has completed.

    Returns:
    - result (int): 1 if the operation is complete, 0 otherwise
    """
    result = self.b1500.query("*OPC?")  # Query operation complete status
    result = result.strip()  # Remove any extra whitespace or termination characters
    result = int(result)  # Convert response to an integer

    return result
