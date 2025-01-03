import importlib
import os
import glob
import pyvisa # Controlling b1500
import ctypes as ct # Convert between python and C data types (needed for WGFMU)
import numpy as np
import time
import matplotlib.pyplot as plt


class B1500_SMU:
    def __init__( self , gpib_address , smu_channel_list , timeout=200000 , DEBUG_PRINT=False ):
        
        self.gpib_address = gpib_address
        self.gpib_str = f"GPIB0::{gpib_address}::INSTR"
        self.smus = smu_channel_list.copy()
        self.rm = pyvisa.ResourceManager()
        
        self.b1500 = self.rm.open_resource( self.gpib_str )
        self.b1500.timeout = timeout
        self.timeout_max = 2000000 # maximum timeout for the b1500 VISA resource manager
        self.b1500.write("*rst; status:preset; *cls")
        
        self.DEBUG_PRINT = DEBUG_PRINT
        
        b1500_query = self.b1500.query("*IDN?")
        print(f"b1500 is bound to {b1500_query}")

    def core_method(self):
        return "This is a core method of B1500Core."

    @staticmethod
    def load_methods():
        """Dynamically load methods from Methods/ and its subfolders."""
        base_path = os.path.dirname(__file__)  # Path to B1500_SMU
        methods_path = os.path.join(base_path, "Methods")

        # Recursively find all Python files in Methods/ and subfolders
        for file in glob.glob(f"{methods_path}/**/*.py", recursive=True):
            if file.endswith("__init__.py"):
                continue  # Skip __init__.py files
            
            # Convert file path to module name
            relative_path = os.path.relpath(file, base_path)
            module_name = relative_path.replace(os.sep, ".")[:-3]  # Remove ".py"
            
            # Dynamically import the module
            module = importlib.import_module(f"B1500_SMU.{module_name}")
            
            # Add all callable methods from the module to the class
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if callable(attr):  # Ensure it's a function
                    setattr(B1500_SMU, attr_name, attr)  # Add to the class

# Dynamically load methods during class definition
B1500_SMU.load_methods()
