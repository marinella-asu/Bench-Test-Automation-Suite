def connect_smu_list(self, smu_num_list):
    """
    Connects one or more SMUs by turning their output switches ON.

    Parameters:
    - smu_num_list (int or list): SMU channel numbers to connect

    Returns:
    - conn_str (str): Command sent to B1500
    """
    # Convert single integer input into a list
    if isinstance(smu_num_list, int):
        smu_num_list = [smu_num_list]

    # Convert SMU numbers to their respective channel strings
    smu_arr = [str(self.smus[smu_num - 1]) for smu_num in smu_num_list]
    smu_str = ",".join(smu_arr)

    # Construct and send connect command
    conn_str = f"CN {smu_str}"  
    self.b1500.write(conn_str)  

    return conn_str
