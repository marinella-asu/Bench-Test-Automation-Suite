def check_err(self, debug_code=""):
    """
    Queries the B1500 for error messages.

    Parameters:
    - debug_code (str): Optional debug message prefix

    Returns:
    - results (str): Error message from the B1500
    """
    self.b1500.write("ERR?")  # Request the error status
    results = self.b1500.read()  # Read the error message
    results = results.strip()  # Clean up the response

    # Format error message for readability
    results_print = results.replace(",", "\t")  
    print(f"{debug_code}{results_print}")  # Print error message with debug code

    return results
