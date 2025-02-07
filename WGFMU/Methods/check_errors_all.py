import ctypes as ct  # Import C types for handling low-level interactions
import wgfmu_consts as wgc  # Import constants for controlling WGFMU

def check_errors_all(self, step_label=None, display_errors=True):
    """
    Checks for all errors in the WGFMU and retrieves error messages if any exist.

    Args:
        step_label (str, optional): A label for the step where errors occurred. Defaults to None.
        display_errors (bool, optional): If True, prints errors to the console. Defaults to True.

    Returns:
        list: A list containing all error messages retrieved from the WGFMU.
    """
    error_detected = False  # Flag to track if errors are found
    error_messages = []  # List to store error messages

    while not error_detected:  # Keep checking until no more errors exist
        error_size = ct.c_int(1)  # Create a C integer to store error size
        self.wg.WGFMU_getErrorSize(ct.byref(error_size))  # Retrieve the size of the error message
        
        if error_size.value > 0:  # If an error exists
            error_buffer = ct.create_string_buffer(error_size.value + 1)  # Create a buffer for error message
            self.wg.WGFMU_getError(ct.byref(error_buffer), ct.byref(error_size))  # Retrieve the actual error message
            
            error_text = error_buffer.value.decode('ascii')  # Convert message from bytes to string
            error_text = error_text.replace("\n", "\t")  # Replace newlines with tabs for readability
            error_messages.append(error_text)  # Store the error message
            
            if display_errors:  # If printing is enabled, display the error
                print(f"{step_label or ''}{error_text}")  # Print step label (if provided) and error message
        
        else:
            error_detected = True  # No more errors to retrieve, exit loop

    return error_messages  # Return list of collected error messages
