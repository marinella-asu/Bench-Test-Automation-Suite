import importlib
import os
import glob
import pyvisa # Controlling b1500
import ctypes as ct # Convert between python and C data types (needed for WGFMU)
import numpy as np
import time
import matplotlib.pyplot as plt
import wgfmu_consts as wgc

class WGFMU:
    def __init__(self, instrument, wgfmus, gpib_address):
        """
        Initializes the B1500 WGFMU object.

        Args:
            instrument: PyVISA instrument instance shared with SMU.
        """
        self.b1500 = instrument
        self.wgfmus = wgfmus
        self.wg = self._load_wgfmu_library() # UNCHECK THIS WHEN YOU ARE ON THE ACTUAL MACHINE THIS JSUT DOESNT WORK ON MY LAPTOP SO ITS COMMENTED OUT

        self.wgc = wgc
        self.wgfmu_gpib_str = ct.create_string_buffer( bytes( f"GPIB0::{gpib_address}::INSTR" , 'utf-8' ) )
        
        # heres your Current Range Constants its just self.c then your range like 1ua or 10ma
        self.c1ua   = wgc.WGFMU_MEASURE_CURRENT_RANGE_1UA 
        self.c10ua  = wgc.WGFMU_MEASURE_CURRENT_RANGE_10UA
        self.c100ua = wgc.WGFMU_MEASURE_CURRENT_RANGE_100UA
        self.c1ma   = wgc.WGFMU_MEASURE_CURRENT_RANGE_1MA
        self.c10ma  = wgc.WGFMU_MEASURE_CURRENT_RANGE_10MA

        self.load_methods()


    def _load_wgfmu_library(self):
        """Loads the WGFMU library (wgfmu.dll) dynamically."""
        # Get the directory of this script (B1500_WGFMU_Core.py)
        base_dir = os.path.dirname(os.path.abspath(__file__))

        # Construct the relative path to the DLL file
        dll_path = os.path.join(base_dir, "wgfmu_x64", "wgfmu.dll")

        # Ensure the DLL exists before loading
        if not os.path.exists(dll_path):
            raise FileNotFoundError(f"WGFMU library not found: {dll_path}")

        # Load the DLL
        try:
            return ct.cdll.LoadLibrary(dll_path)
        except Exception as e:
            raise RuntimeError(f"Failed to load WGFMU DLL: {e}")
        
    def core_method(self):
        return "This is a core method of B1500CoreWGFMU."

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
            module = importlib.import_module(f"WGFMU.{module_name}")
            
            # Add all callable methods from the module to the class
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if callable(attr):  # Ensure it's a function
                    setattr(WGFMU, attr_name, attr)  # Add to the class

