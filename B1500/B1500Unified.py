from SMU.B1500_SMU_Core import SMU
from WGFMU.B1500_WGFMU_Core import WGFMU
import ctypes as ct # Convert between python and C data types (needed for WGFMU)
from TestInfo.TestInfo import TestInfo
import pyvisa


class B1500:
    def __init__(self, gpib_address = 17, smu_channels= [301, 401, 501, 601], wgfmu_channels = [101, 102],  parameters=None, timeout=200000):
        """
        Initializes the B1500 unified interface, including shared resource management
        for SMUs and WGFMUs, and a TestInfo object for parameter handling.

        Args:
            gpib_address (int): GPIB address for the B1500.
            smu_channels (list): List of SMU channels to initialize.
            parameters (dict): Initial parameters for the test.
            timeout (int): Timeout in seconds for GUI validation.
        """
        self.gpib_address = gpib_address
        self.smus = smu_channels
        self.wgfmus = wgfmu_channels
        # self.resource_manager = pyvisa.ResourceManager()
        # self.connection = self._connect_to_instrument()
        self.connection = "Connection"

        # Initialize SMU and WGFMU objects
        
        self.smu = SMU(self.connection, self.smus)
        self.wgfmu = WGFMU(self.connection, self.wgfmus)

        # Initialize TestInfo and validate parameters
        self.test_info = TestInfo(parameters or {})
        self.test_info.validate_and_prompt(timeout=timeout)

    def _connect_to_instrument(self):
        """
        Establishes a shared connection to the B1500 using the GPIB address.
        Returns:
            pyvisa.resources.Resource: A shared connection to the B1500.
        """
        gpib_str = f"GPIB0::{self.gpib_address}::INSTR"
        connection = self.resource_manager.open_resource(gpib_str)
        connection.write("*rst; status:preset; *cls")
        print(f"Connected to B1500 at {self.gpib_address}")
        return connection

    def save_data(self, data, file_path, column_labels=None):
        """
        Saves test parameters and data into a CSV file.
        Args:
            data (dict): Test data with column names as keys and lists as values.
            file_path (str): Path to save the CSV.
            column_labels (list): Optional custom column labels for the data.
        """
        import csv

        with open(file_path, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)

            # Write parameters as a description
            writer.writerow(["Parameter", "Value"])
            for key, value in self.test_info.parameters.items():
                writer.writerow([key, value])
            writer.writerow([])  # Blank line between parameters and data

            # Write data headers
            if column_labels:
                writer.writerow(column_labels)
            else:
                writer.writerow(data.keys())

            # Write data rows
            rows = zip(*data.values())
            for row in rows:
                writer.writerow(row)

        print(f"Test data saved to {file_path}.")

    @staticmethod
    def data_cleaner(raw_data):
        """
        Placeholder for data cleaning logic.
        Args:
            raw_data: Raw data from the B1500.
        Returns:
            dict: Cleaned data with column names as keys and lists as values.
        """
        print("Data cleaner placeholder. Add your data cleaning logic here.")
        return raw_data  # Modify this to implement your cleaning logic
