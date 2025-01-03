import importlib
import os
import glob
import pyvisa # Controlling b1500
import ctypes as ct # Convert between python and C data types (needed for WGFMU)
import numpy as np
import time
import matplotlib.pyplot as plt


class B1500_WGFMU:
    def __init__( self , b1500_gpib_address , wgfmu_channel_list , wgfmu_dll_path = "wgfmu_x64\wgfmu.dll" ):
        #WGFMU Library Locations
        #wgfmu_dll_path = "wgfmu_x64\wgfmu.dll"
        #wgfmu_h_path = "wgfmu_x64\wgfmu.h"
        #wgfmu_lib_path = "wgfmu_x64\wgfmu.lib"
        
        # Communicaton Channels for your B1500
        self.b1500_gpib_address = b1500_gpib_address
        
        # Channel IDs for the various modules you want to control
        #   slot channels are <slot_number>0<subslotnumber>.
        #   so look at the back of your b150 and get the slot numbers for everything!
        #   the thing in slot 1 can be addressed as 101
        #   some cards may have multiple submodules (e.g. the WGFMU). In this case each submodule is addressed sequentially
        #   so a WGFMU in slot 2 would have WGFMU1 on channel 201, WGFMU2 on channel 202.
        #wgfmu_channel_1 = 201
        #wgfmu_channel_2 = 202
        #wgfmu_channel_3 = 301
        #wgfmu_channel_4 = 302
        
        self.wgfmus = wgfmu_channel_list.copy()
        
        self.b1500_gpib_str = f"GPIB0::{self.b1500_gpib_address}::INSTR"
        self.wgfmu_gpib_str = ct.create_string_buffer( bytes( self.b1500_gpib_str , 'utf-8' ) )
        
        # This loads the WGFMU dll
        # The dll contains all the handles to the C++ functions we will need to use to control the WGFMU
        self.wg = ct.cdll.LoadLibrary( wgfmu_dll_path )

        

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
            module = importlib.import_module(f"B1500_WGFMU.{module_name}")
            
            # Add all callable methods from the module to the class
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if callable(attr):  # Ensure it's a function
                    setattr(B1500_WGFMU, attr_name, attr)  # Add to the class

# Dynamically load methods during class definition
B1500_WGFMU.load_methods()
