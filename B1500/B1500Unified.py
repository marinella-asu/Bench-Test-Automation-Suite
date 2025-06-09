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
import wgfmu_consts as wgc
from typing import Any, Dict

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

# Define configurations for each B1500 unit
B1500_CONFIG = {
    "A": {"gpib_address": 17, "smu_channels": [301, 401, 501, 601], "wgfmu_channels": [201, 202]},
    "B": {"gpib_address": 18, "smu_channels": [302, 402, 502, 602], "wgfmu_channels": [103, 104]}, #Change
    "C": {"gpib_address": 19, "smu_channels": [303, 403, 503, 603], "wgfmu_channels": [105, 106]}, #Change 
    "D": {"gpib_address": 20, "smu_channels": [304, 404, 504, 604], "wgfmu_channels": [107, 108]}, #Change
}

   

class B1500:
    def __init__(self, parameters, unit_label = None, gpib_address = 17, smu_channels= [301, 401, 501, 601], wgfmu_channels = [101, 102], timeout=200000):
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

        if unit_label is not None:
            if unit_label not in B1500_CONFIG:
                raise ValueError(f"❌ Invalid B1500 unit label '{unit_label}'. Choose from: A, B, C, or D.")

            # Load configuration for the selected unit
            config = B1500_CONFIG[unit_label]
            self.gpib_address = config["gpib_address"]
            self.smus = config["smu_channels"]
            self.wgfmus = config["wgfmu_channels"]

            # Display configuration for verification
            print(f"🔧 Initializing B1500 Unit {unit_label}")
            print(f"📡 GPIB Address: {self.gpib_address}")
            print(f"🔌 SMU Channels: {self.smus}")
            print(f"⚡ WGFMU Channels: {self.wgfmus}")

        
        self.resource_manager = pyvisa.ResourceManager()
        self.connection = self._connect_to_instrument()
        self.connection.timeout = 200000
        
        # self.connection = "Connection" # THIS IS JUST FOR A TEST PLEASE CHANGE THIS FOR THE RELEASE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        
        # Initialize SMU and WGFMU objects
        
        self.smu = SMU(self.connection, self.smus)
        # self.wgfmu = WGFMU(self.connection, self.wgfmus, self.gpib_address)

        # Initialize TestInfo and validate parameters
        self.test_info = TestInfo(parameters or {})
        self.test_info.validate_and_prompt(timeout=timeout)
        self.parameters = parameters

        # Setup waveform channel mapping if VDD WGFMU is defined
        self.test_info.VDD_WGFMU = int(self.test_info.parameters.get("VDD WGFMU", 1))
        if self.test_info.VDD_WGFMU == 1:
            self.test_info.ch_vdd = self.wgfmu.wgfmus[0]
            self.test_info.ch_vss = self.wgfmu.wgfmus[1]
        else:
            self.test_info.ch_vdd = self.wgfmu.wgfmus[1]
            self.test_info.ch_vss = self.wgfmu.wgfmus[0]


        # VDD_waveform_data = self.test_info.parameters.get("VDD Waveform Data", None)
        # VSS_waveform_data = self.test_info.parameters.get("VSS Waveform Data", None)
        # if VDD_waveform_data:
        #     self.VDD_T_values = VDD_waveform_data["Time"]
        #     self.VDD_V_values = VDD_waveform_data["Voltage"]
        #     print(f"Loaded waveform with {len(self.VDD_T_values)} points.")
        # else:
        #     print("No waveform data found.")
        # if VSS_waveform_data:
        #     self.VSS_T_values = VSS_waveform_data["Time"]
        #     self.VSS_V_values = VSS_waveform_data["Voltage"]
        #     print(f"Loaded waveform with {len(self.VSS_T_values)} points.")
        # else:
        #     print("No waveform data found.")

    def __getattr__(self, name):
        # this allows dynamic access to variables in the parameters
        #Example b1500.Name will return test_info.parameters["Name"]
        
        if name in self.test_info.parameters:
            return self.test_info.parameters[name]
        raise AttributeError(f"'B1500' Object has no attribute '{name}'")
        
    def _connect_to_instrument(self):
        """
        Establishes a shared connection to the B1500 using the GPIB address.
        Returns:
            pyvisa.resources.Resource: A shared connection to the B1500.
        """
        gpib_str = f"GPIB0::{self.gpib_address}::INSTR"
        connection = self.resource_manager.open_resource(gpib_str)
        connection.read_termination = "\r\n"  # Sets the character that indicates the end of a read
        connection.write_termination = "\r\n"  # Optional: sets the character appended to a write

        ID = connection.query("*IDN?")
        print(f"Connected to {ID} at {self.gpib_address}")
        return connection

    def _get_final_params(defaults: Dict[str, Any],
                        block: Dict[str, Any],
                        overrides: Dict[str, Any]) -> Dict[str, Any]:
        """Return one dict where caller overrides > block > library defaults."""
        params = defaults.copy()
        params.update(block)       # second priority
        params.update(overrides)   # highest priority
        return params

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



    def data_clean(self, raw_data, parameters, NoSave = False):
        """
        Cleans and structures raw B1500 output data, mapping it to the correct SMU/WGFMU channels.
        Saves the cleaned data into both a structured CSV file and a TXT file inside the 'data/' directory.

        Args:
            raw_data (str): The raw ASCII data string from the B1500 instrument.
            parameters (dict): Dictionary containing test parameters (e.g., "Name", "Test Number", etc.)

        Returns:
            dict: A dictionary containing structured NumPy arrays for each unit type.
        """
        # print("🔄 Starting data_clean method...")

        


        # Split raw data string into individual entries
        entries = raw_data.strip().split(",")
        # print(f"🔍 Raw Data Entries Count: {len(entries)}")
        # print(f"📜 First 10 Entries: {entries[:10]}")

        # Identify SMU and WGFMU channels from the B1500 object
        channel_lookup = {ch: f"SMU{i+1}" for i, ch in enumerate(self.smus)}
        channel_lookup.update({ch: f"WGFMU{i+1}" for i, ch in enumerate(self.wgfmus)})
        # print(f"📡 Channel Lookup Table: {channel_lookup}")

        # Regex pattern to extract unit code and value
        pattern = re.compile(r"([A-Z][a-zA-Z]{2})([+-]\d+\.\d+E[+-]\d+)")

        # Process each entry
        temp_data = []
        for entry in entries:
            match = pattern.match(entry)
            if not match:
                print(f"⚠️ Skipping malformed entry: {entry}")
                continue

            unit_code, value = match.groups()
            # print(f"🛠️ Extracted Unit Code: {unit_code}, Value: {value}")
# 
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

            # Column naming: e.g., SMU1_Voltage, WGFMU1_Current
            column_name = f"{mapped_channel}_{unit_type.split()[0]}"
            temp_data.append([status, mapped_channel, unit_type, value, column_name])

        # print(f"✅ Parsed Data Count: {len(temp_data)}")
        if not temp_data:
            print("❌ No valid data extracted. Check raw data format.")
            return {}

        # Convert parsed data to DataFrame
        df = pd.DataFrame(temp_data, columns=["Status", "Module", "Unit", "Value", "Column_Name"])
        # print("📝 Initial DataFrame Preview:")
        # print(df.head(10))

        # Pivot DataFrame so each module-unit pair becomes a unique column
        df["Measurement"] = df.groupby(["Module", "Unit"]).cumcount()
        df_pivot = df.pivot(index="Measurement", columns="Column_Name", values="Value")

        # print("📊 Pivoted DataFrame Preview:")
        # print(df_pivot.head(10))
        
        if not NoSave:
            # Extract parameter values dynamically
            experimenter = parameters.get("Name", "Unknown_Experimenter")
            test_number = parameters.get("Test Number", "Unknown_Test")
            die_number = parameters.get("Die Number", "Unknown_Die")
            device_number = parameters.get("Device Number", "Unknown_Device")

            # Locate "Bench_Test_Automation_Suite" folder dynamically
            script_dir = os.path.dirname(os.path.abspath(__file__))
            while not script_dir.endswith("Bench-Test-Automation-Suite-main"):
                script_dir = os.path.dirname(script_dir)  # Move up one level

            # Ensure the data is stored inside "Bench_Test_Automation_Suite/Data"
            base_dir = os.path.join(script_dir, "Data", experimenter)
            os.makedirs(base_dir, exist_ok=True)

            # Generate filenames
            date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            file_basename = f"{test_number}_Die{die_number}_Device{device_number}_{date_str}"
            csv_filepath = os.path.join(base_dir, file_basename + ".csv")
            txt_filepath = os.path.join(base_dir, file_basename + ".txt")

            print(f"📂 Saving CSV to: {csv_filepath}")
            print(f"📂 Saving TXT to: {txt_filepath}")
            # ---- Write Clean CSV File ----
            with open(csv_filepath, "w") as f:
                # Write metadata as comments
                for key, value in parameters.items():
                    f.write(f"# {key}: {value}\n")
                f.write("\n")  # Blank line before actual data
                df_pivot.to_csv(f)

            # ---- Write Clean TXT File ----
            with open(txt_filepath, "w") as f:
                # Write metadata in a structured "box" format
                max_key_length = max(len(k) for k in parameters.keys())
                f.write("=" * (max_key_length + 20) + "\n")
                for key, value in parameters.items():
                    f.write(f"{key.ljust(max_key_length)}: {value}\n")
                f.write("=" * (max_key_length + 20) + "\n\n")

                # Write the data in a readable format
                df_pivot.to_csv(f, sep="\t")
            
            print(f"✅ Data cleaned and saved to: {csv_filepath} and {txt_filepath}")

       

        # Convert DataFrame into structured NumPy arrays
        output_data = {}
        for column in df_pivot.columns:
            unit_array = df_pivot[column].to_numpy()
            output_data[column] = unit_array
            # print(f"📦 Extracted NumPy Array for {column}: {unit_array.shape}")

        return output_data
    

    def save_numpy_to_csv(self, TestInfo, array, filename = "Saved"):
        """
        Saves a NumPy array as a CSV file in the Data directory using the experimenter's name.

        Parameters:
        - array (numpy.ndarray): The NumPy array to be saved.
        - filename (str): The desired base filename (without extension).
        - TestInfo (object): Object containing test parameters, including "Name".

        Returns:
        - str: Full path to the saved CSV file.
        """
        print("🔄 Starting save_numpy_to_csv method...")

        # Get experimenter's name
        experimenter = TestInfo.parameters.get("Name", "Unknown_Experimenter")

        # Locate "Bench_Test_Automation_Suite" folder dynamically
        script_dir = os.path.dirname(os.path.abspath(__file__))
        while not script_dir.endswith("Bench-Test-Automation-Suite-main"):
            script_dir = os.path.dirname(script_dir)  # Move up one level

        # Ensure the data is stored inside "Bench_Test_Automation_Suite/Data"
        base_dir = os.path.join(script_dir, "Data", experimenter)
        os.makedirs(base_dir, exist_ok=True)

        # Generate timestamped filename
        date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        csv_filepath = os.path.join(base_dir, f"{filename}_{date_str}.csv")

        np.savetxt(csv_filepath, array, delimiter=",", fmt="%.10e")


        print(f"✅ NumPy array saved to: {csv_filepath}")

        return csv_filepath
