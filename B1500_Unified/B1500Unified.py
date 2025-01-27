from B1500_SMU.B1500_SMU_Core import B1500SMU
from B1500_WGFMU.B1500_WGFMU_Core import B1500WGFMU
from TestInfo.TestInfo import TestInfo
import pyvisa


class B1500Unified:
    def __init__(self, gpib_address, modules = "both", smu_channels=None, parameters=None, timeout=200000):
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
        self.smu_channels = smu_channels or [301, 401, 501, 601] # default for GWC 331
        self.resource_manager = pyvisa.ResourceManager()
        self.connection = self._connect_to_instrument()

        # Initialize SMU and WGFMU objects
        if (modules == "both"):
            self.b1500_smu = B1500SMU(self.connection, self.smu_channels)
            self.b1500_wgfmu = B1500WGFMU(self.connection) # FIX THIS FOR WGFMU!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!            
        self.b1500_smu = B1500SMU(self.connection, self.smu_channels) if modules == "SMU" else None
        self.b1500_wgfmu = B1500WGFMU(self.connection) if modules == "WGFMU" else None

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
        self.b1500.write("*rst; status:preset; *cls")
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
