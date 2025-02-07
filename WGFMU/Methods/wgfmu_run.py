import ctypes as ct  # Import C types for low-level hardware interaction
import time  # Import time module for delays
import wgfmu_consts as wgc  # Import constants for WGFMU operations

def wgfmu_run(self, timeout_seconds=5):
    """
    Executes the WGFMU sequence and waits for completion.

    Args:
        timeout_seconds (int, optional): Maximum wait time for the sequence to complete. Defaults to 5 seconds.

    Returns:
        bool: True if the execution completes successfully, False if a timeout occurs.
    """
    # Start execution of WGFMU sequence
    self.wg.WGFMU_execute()

    elapsed_time = 0  # Initialize timer to track execution time
    is_complete = ct.c_int(0)  # C integer to hold execution status

    # Loop until execution completes or timeout is reached
    while elapsed_time < timeout_seconds:
        self.wg.WGFMU_getExecutionStatus(ct.byref(is_complete))  # Get execution status
        if is_complete.value == wgc.WGFMU_EXECUTION_STATUS_DONE:  # Check if execution is complete
            return True  # Execution completed successfully
        time.sleep(0.1)  # Wait before checking again
        elapsed_time += 0.1  # Increment elapsed time

    # If execution does not complete within timeout, return False
    return False
