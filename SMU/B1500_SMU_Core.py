import importlib
import os
import glob
import ctypes as ct # Convert between python and C data types (needed for WGFMU)
import numpy as np
import time
import matplotlib.pyplot as plt
import inspect


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

    def _resolve_params(self, method_name: str, b1500, override_params: dict = {}):
        """Extract parameters from b1500.parameters using method_name and allow overrides."""
        param_block = b1500.parameters.get(method_name, {})
        
        # Also attach as individual attributes like: b1500.vstart_MethodName
        for key, value in param_block.items():
            setattr(b1500, f"{key}_{method_name}", value)

        # Get the actual method name calling this (e.g., 'smu_meas_sample_multi_term')
        frame = inspect.currentframe().f_back
        func_name = frame.f_code.co_name
        func = getattr(self, func_name)
        sig = inspect.signature(func)

        args = {}
        for param in sig.parameters:
            if param == 'self':
                continue
            # Priority: overrides > param_block > b1500.<varname_methodname>
            args[param] = (
                override_params.get(param) or
                param_block.get(param) or
                getattr(b1500, f"{param}_{method_name}", None)
            )
        return args

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

