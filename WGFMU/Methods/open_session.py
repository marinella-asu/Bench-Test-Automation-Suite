import ctypes as ct  # Import C types for low-level API calls
import wgfmu_consts as wgc  # Import constants for WGFMU operations

def open_session(self):
    """
    Initializes a new WGFMU session.

    Returns:
        bool: True if the session is successfully opened, False otherwise.
    """
    return_code = self.wg.WGFMU_openSession()  # Open a new session with WGFMU

    if return_code == wgc.WGFMU_NO_ERROR:  # Check if the session opened without errors
        return True  # Successfully opened session
    else:
        self.check_error_status(return_code, step_id="Opening WGFMU Session")  # Log the error
        return False  # Session failed to open
