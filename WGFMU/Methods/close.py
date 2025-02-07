import wgfmu_consts as wgc  # Import constants for WGFMU operations

def close(self):
    """
    Closes the WGFMU session.

    Returns:
        bool: True if the session was successfully closed, False otherwise.
    """
    return_code = self.wg.WGFMU_closeSession()  # Close WGFMU session

    if return_code == wgc.WGFMU_NO_ERROR:  # Check if the operation succeeded
        return True
    else:
        self.check_error_status(return_code, step_id="Closing WGFMU Session")
        return False
