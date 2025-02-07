def reset(self):
    """
    Resets the B1500 to its initial settings.
    """
    self.b1500.write("*RST; STATUS:PRESET; *CLS")  # Reset, preset status, clear errors
