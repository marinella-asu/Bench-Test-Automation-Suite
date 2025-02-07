def bias_smu(self, smu_num, voltage, Icomp=100e-3):
    """
    Applies a DC bias voltage to a specified SMU.

    Parameters:
    - smu_num (int): SMU channel number
    - voltage (float): Voltage to apply
    - Icomp (float): Compliance current limit (default: 100mA)

    Returns:
    - None
    """
    smu_ch = self.smus[smu_num - 1]  # Get SMU channel number

    # Construct voltage bias command
    bias = f"DV {smu_ch},0,{voltage},{Icomp:.3E}"  

    # Send voltage bias command to the B1500
    self.b1500.write(bias)  
