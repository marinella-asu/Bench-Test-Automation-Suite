def zero_smus(self):
    """Resets all SMUs to 0V output."""
    self.b1500.write("DZ")
