import ctypes as ct  # Import C types for handling low-level interactions
import wgfmu_consts as wgc  # Import constants for controlling WGFMU

def check_errors(self, return_code=-1, step_id=-1):
    """
    Checks if an error occurred and retrieves the corresponding error message.

    Args:
        return_code (int, optional): Return code from the last WGFMU operation. Defaults to -1.
        step_id (int, optional): Identifier for the step where the error occurred. Defaults to -1.

    Returns:
        int: The original return code (unchanged).
    """
    if return_code != wgc.WGFMU_NO_ERROR:  # If the return code is not "No Error", check for issues
        error_size = ct.c_int(1)  # Create a C integer to store the error size
        self.wg.WGFMU_getErrorSize(ct.byref(error_size))  # Retrieve the size of the error message
        
        if error_size.value > 0:  # If an error exists
            error_buffer = ct.create_string_buffer(error_size.value + 1)  # Create a buffer for error message
            self.wg.WGFMU_getError(ct.byref(error_buffer), ct.byref(error_size))  # Retrieve the actual error message
            
            error_text = error_buffer.value.decode('utf-8')  # Convert message from bytes to string
            
            if step_id > 0:  # If a step ID is provided, format output with the step ID
                print(f"Step {step_id}: {error_text}")
            else:  # If no step ID, just print the error message
                print(error_text)
    
    return return_code  # Return the original return code unchanged
