from SMU.B1500_SMU_Core import SMU
from WGFMU.B1500_WGFMU_Core import WGFMU
import ctypes as ct # Convert between python and C data types (needed for WGFMU)
from TestInfo.TestInfo import TestInfo
import pyvisa
import os
import numpy as np
import pandas as pd
from datetime import datetime
 # Unit type mapping from the provided table
import os
import numpy as np
import pandas as pd
from datetime import datetime
import re

# Unit type mapping from the B1500 documentation
UNIT_MAP = {
    "V": "Voltage (V)", "I": "Current (A)", "F": "Frequency (Hz)",
    "Z": "Impedance (Ω)", "Y": "Admittance (S)", "C": "Capacitance (F)",
    "L": "Inductance (H)", "R": "Phase (radian)", "P": "Phase (degree)",
    "D": "Dissipation Factor", "Q": "Quality Factor", "X": "Sampling Index",
    "T": "Time (s)"
}

STATUS_CODES = {
    "N": "No Error", "T": "Compliance Reached (Other Channel)", "C": "Compliance Reached",
    "V": "Over Measurement Range", "X": "Oscillating Output", "F": "Force Saturation",
    "G": "Search Target Not Found", "S": "Search Stopped", "U": "Null Loop Unbalance",
    "D": "IV Amplifier Saturation", "W": "First/Intermediate Sweep Step", "E": "Last Sweep Step"
}

# Subchannel mapping (slots 1-10, subchannels 1-2)
CHANNEL_MAP = {
    "A": 101, "B": 201, "C": 301, "D": 401, "E": 501, "F": 601, "G": 701, "H": 801, "I": 901, "J": 1001,
    "a": 102, "b": 202, "c": 302, "d": 402, "e": 502, "f": 602, "g": 702, "h": 802, "i": 902, "j": 1002
}


   

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



    def data_clean(self, raw_data):
        """
        Cleans and structures raw B1500 output data, mapping it to the correct SMU/WGFMU channels.
        Saves the cleaned data into a structured CSV file inside the 'data/' directory.

        Args:
            raw_data (str): The raw ASCII data string from the B1500 instrument.

        Returns:
            dict: A dictionary containing structured NumPy arrays for each unit type.
        """
        print("🔄 Starting data_clean method...")

        if not hasattr(self, "test_info") or not self.test_info:
            raise ValueError("B1500 object is missing TestInfo parameters.")

        test_info = self.test_info
        experimenter = test_info.parameters.get("Name", "Unknown_Experimenter")
        test_number = test_info.parameters.get("Test Number", "Unknown_Test")
        die_number = test_info.parameters.get("Die Number", "Unknown_Die")
        device_number = test_info.parameters.get("Device Number", "Unknown_Device")

        # Create a structured output directory
        date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        base_dir = os.path.join("data", experimenter)
        os.makedirs(base_dir, exist_ok=True)

        csv_filename = f"{test_number}_Die{die_number}_Device{device_number}_{date_str}.csv"
        csv_filepath = os.path.join(base_dir, csv_filename)

        print(f"📂 Saving CSV to: {csv_filepath}")

        # Store parsed data
        parsed_data = []

        # Split raw data string into individual entries
        entries = raw_data.strip().split(",")

        print(f"🔍 Raw Data Entries Count: {len(entries)}")
        print(f"📜 First 10 Entries: {entries[:10]}")

        # Identify SMU and WGFMU channels from the B1500 object
        channel_lookup = {ch: f"SMU{i+1}" for i, ch in enumerate(self.smus)}
        channel_lookup.update({ch: f"WGFMU{i+1}" for i, ch in enumerate(self.wgfmus)})

        print(f"📡 Channel Lookup Table: {channel_lookup}")

        # Process each entry
        pattern = re.compile(r"([A-Z][a-zA-Z]{2})([+-]\d+\.\d+E[+-]\d+)")

        temp_data = []  # Store each measurement as a separate row
        for entry in entries:
            match = pattern.match(entry)
            if not match:
                print(f"⚠️ Skipping malformed entry: {entry}")
                continue  # Skip malformed entries

            unit_code, value = match.groups()

            print(f"🛠️ Extracted Unit Code: {unit_code}, Value: {value}")

            # Extract status, channel, and unit
            status = STATUS_CODES.get(unit_code[0], "Unknown Status")
            channel_identifier = unit_code[1]
            unit_type = UNIT_MAP.get(unit_code[2], f"Unknown Unit ({unit_code[2]})")

            # Map channel identifier to SMU/WGFMU name
            channel_number = CHANNEL_MAP.get(channel_identifier, None)
            mapped_channel = channel_lookup.get(channel_number, None)

            if not mapped_channel:
                print(f"❌ Unrecognized Channel Identifier: {channel_identifier} (Skipping entry)")
                continue

            # New Column Name Format: SMU1_Voltage, SMU2_Current, WGFMU1_Time, etc.
            column_name = f"{mapped_channel}_{unit_type.split()[0]}"  # Extracts first word from unit type

            temp_data.append([status, mapped_channel, unit_type, value, column_name])

        print(f"✅ Parsed Data Count: {len(temp_data)}")
        if not temp_data:
            print("❌ No valid data extracted. Check raw data format.")
            return {}

        # Convert parsed data to DataFrame
        df = pd.DataFrame(temp_data, columns=["Status", "Module", "Unit", "Value", "Column_Name"])

        print("📝 Initial DataFrame Preview:")
        print(df.head(10))

        # Pivot so each module-unit pair becomes a unique column
        df["Measurement"] = df.groupby(["Module", "Unit"]).cumcount()  # Creates a unique index per measurement
        df_pivot = df.pivot(index="Measurement", columns="Column_Name", values="Value")

        print("📊 Pivoted DataFrame Preview:")
        print(df_pivot.head(10))

        # Write clean CSV
        df_pivot.to_csv(csv_filepath)

        print(f"✅ Data cleaned and saved to: {csv_filepath}")

        # Convert DataFrame into structured NumPy arrays
        output_data = {}
        for column in df_pivot.columns:  # Loop through all unique measurement columns
            unit_array = df_pivot[column].to_numpy()  # Convert to NumPy array
            output_data[column] = unit_array  # Store with proper labeling

            print(f"📦 Extracted NumPy Array for {column}: {unit_array.shape}")

        return output_data