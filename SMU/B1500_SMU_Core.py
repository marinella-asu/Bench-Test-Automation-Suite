import importlib
import os
import glob
import pyvisa # Controlling b1500
import ctypes as ct # Convert between python and C data types (needed for WGFMU)
import numpy as np
import time
import matplotlib.pyplot as plt


class SMU:
    def __init__(self, instrument, smus):
        super().__init__() 
        """
        Initializes the B1500 SMU object.

        Args:
            instrument: PyVISA instrument instance shared with WGFMU.
        """
        self.b1500 = instrument
        self.smus = smus
        self.load_methods()

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
            module = importlib.import_module(f"SMU.{module_name}")
            
            # Add all callable methods from the module to the class
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if callable(attr):  # Ensure it's a function
                    setattr(SMU, attr_name, attr)  # Add to the classsuper().__init__() 

