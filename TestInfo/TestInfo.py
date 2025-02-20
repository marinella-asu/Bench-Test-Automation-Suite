import os
import tkinter as tk
from tkinter import messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import wgfmu_consts as wgc
import pandas as pd

class TestInfo:
    def __init__(self, parameters=None):
        """
        Initializes TestInfo with parameters.
        Args:
            parameters (dict): Dictionary of parameters with their default values.
        """
        self.parameters = parameters or {}
        

    def validate_and_prompt(self, timeout=300):
        """
        Validates parameters and prompts the user to fill missing ones via a GUI.
        """
        missing_params = {k: v for k, v in self.parameters.items() if v in [None, "ask"] and k not in ["Waveform", "Waveform Format", "Waveform Editor"]}

        # List of waveform-related keys to exclude
        waveform_keys = {"Waveform", "Waveform Editor"}

        # Dynamically assign parameters as attributes
        for key, value in self.parameters.items():
            if key not in waveform_keys:  # Exclude waveform-related parameters
                safe_key = key.replace(" ", "_")  # Convert spaces to underscores
                setattr(self, safe_key, value)  # Assign as attribute


        if missing_params:
            self.prompt_user_for_parameters(missing_params, timeout)

        # Handle waveform input AFTER parameter validation
        if "Waveform Editor" in self.parameters:
            self.handle_VDD_waveform()
        # if "VSS Waveform" in self.parameters:
        #     self.handle_VSS_waveform()

    def prompt_user_for_parameters(self, missing_params, timeout):
        """Creates a GUI for the user to input missing parameters."""
        print("Some parameters are missing. Launching GUI...")

        def on_submit():
            for key, entry in entry_widgets.items():
                value = entry.get().strip()
                if value:
                    self.parameters[key] = value
            root.quit()
            root.destroy()

        root = tk.Tk()
        root.title("Parameter Input")
        root.geometry("400x300")

        tk.Label(root, text="Please fill in the required parameters:", font=("Arial", 12)).pack(pady=10)
        entry_widgets = {}

        for param in missing_params:
            frame = tk.Frame(root)
            frame.pack(pady=5, fill="x", padx=10)
            tk.Label(frame, text=f"{param}:", width=20, anchor="w").pack(side="left")
            entry = tk.Entry(frame)
            entry.pack(side="right", fill="x", expand=True)
            entry_widgets[param] = entry

        tk.Button(root, text="Submit", command=on_submit).pack(pady=20)

        root.mainloop()

    def handle_VDD_waveform(self):
        """Handles waveform input, including waveform formats."""
        waveform_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Waveforms")
        format_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Waveforms", "Formats")
        os.makedirs(waveform_folder, exist_ok=True)
        os.makedirs(format_folder, exist_ok=True)

        waveform_param = self.parameters["Waveform"]
        waveform_format = self.parameters.get("Waveform Format", None)
        user_name = self.parameters.get("Name", "User").replace(" ", "_")

        # Load waveform format if specified and new waveform
        format_labels = None
        if waveform_format:
            format_path = os.path.join(format_folder, f"{waveform_format}.txt")
            if self.parameters["Waveform"] == "ask":
                if os.path.exists(format_path):
                    format_labels = self.load_waveform_format(format_path)
                    print(f"✅ Loaded waveform format: {waveform_format}")               
                else:
                    print(f"⚠️ Waveform format {waveform_format} not found.")
            
        waveform_filename = self.parameters["Waveform"]  # Get the filename from parameters
        waveform_filepath = os.path.join(waveform_folder, waveform_filename)

        if self.parameters["Waveform Editor"] == "ask":
            if self.parameters["Waveform"] != "ask":
                if os.path.exists(waveform_folder):
                    old_waveform_data = self.load_waveform(waveform_filepath)
                    print(f"✅ Loaded waveform: {old_waveform_data}")               
                else:
                    print(f"⚠️ Waveform format {waveform_format} not found.")
            print("Launching waveform editor...")
            waveform_data = self.launch_waveform_editor(old_waveform_data = old_waveform_data, labels = None)

            # Determine next available waveform number
            existing_waveforms = [f for f in os.listdir(waveform_folder) if f.startswith(user_name)]
            next_waveform_number = len(existing_waveforms) + 1
            waveform_filename = f"{user_name}_{waveform_format}_{next_waveform_number}.txt" if waveform_format else f"{user_name}_{next_waveform_number}.txt"

            waveform_path = os.path.join(waveform_folder, waveform_filename)
            self.save_waveform(waveform_data, waveform_path)
            self.parameters["Waveform"] = waveform_filename
            print(f"✅ Waveform saved as {waveform_filename}")

        else:
            waveform_path = os.path.join(waveform_folder, f"{waveform_param}.txt")
            if not os.path.exists(waveform_path):
                print(f"⚠️ Waveform {waveform_param} not found. Creating a new one.")
                waveform_data = self.launch_waveform_editor(format_labels)
                self.save_waveform(waveform_data, waveform_path)


    def load_waveform_format(self, format_path):
        """Loads the waveform format file and returns the list of labels."""
        with open(format_path, "r") as f:
            labels = [line.strip() for line in f.readlines()]
        return labels

    def load_waveform(self, file_path):
        """Loads waveform data from a text file into NumPy arrays."""
        if not file_path.endswith(".txt"):  
            file_path += ".txt"  

        if not os.path.exists(file_path):
            print(f"⚠️ Waveform file {file_path} not found. Returning empty arrays.")
            return {}

        try:
            # Load using pandas for better parsing of variable 
            data = pd.read_csv(file_path, sep='\s+', header=None, dtype=str)
            
            if data.shape[1] < 4:
                raise ValueError("File has insufficient columns!")

            labels = data.iloc[:, 0].tolist()
            times = data.iloc[:, 1].astype(float).tolist()
            vdd_voltage = data.iloc[:, 2].tolist()
            vss_voltage = data.iloc[:, 3].tolist()
            compliance = data.iloc[:, 4].fillna("").tolist() if data.shape[1] > 4 else [""] * len(labels)  # Handle missing compliance

            print(f"🔍 Successfully Loaded Waveform Data (First 5 rows):\n{data.head()}")

            return {
                "Labels": labels,
                "VDD Time": times,
                "VSS Time": times,
                "VDD Voltage": vdd_voltage,
                "VSS Voltage": vss_voltage,
                "Compliance": compliance
            }

        except Exception as e:
            print(f"⚠️ Error loading waveform file: {e}")
            return {}




    def save_waveform(self, waveform_data, file_path):
        """Saves waveform data to a text file."""
        if waveform_data:
            np.savetxt(file_path, np.column_stack((
                waveform_data["Labels"],
                waveform_data["VDD Time"],
                waveform_data["VDD Voltage"],
                waveform_data["VSS Voltage"],
                waveform_data["Compliance Literals"]
            )), delimiter="\t", fmt="%s")
        else:
            print("No Waveform No Test")
            exit(1)
        print(f"Waveform saved to {file_path}")

    def launch_waveform_editor(self, old_waveform_data=None, labels = None):
        """Opens the waveform editor GUI with VDD, VSS, and compliance columns."""
        root = tk.Tk()
        root.title("Waveform Editor")
        root.geometry("1200x600")

        Full_labels = labels if labels is not None else old_waveform_data.get("Labels", [])
        times = old_waveform_data.get("VDD Time", []) if old_waveform_data else []
        vdd_voltage = old_waveform_data.get("VDD Voltage", []) if old_waveform_data else []
        vss_voltage = old_waveform_data.get("VSS Voltage", []) if old_waveform_data else []
        compliance = old_waveform_data.get("Compliance", []) if old_waveform_data else []


        if labels is None:
            num_rows = len(Full_labels)  # Ensures minimum 11 rows
        else:
            num_rows = len(labels)  # Ensures minimum 11 rows    
        print(f"number of rows: {num_rows}\n")
        label_entries, time_entries, vdd_entries, vss_entries, compliance_entries = [], [], [], [], []

        frame = tk.Frame(root)
        frame.pack(side=tk.LEFT, padx=10, pady=10)

        headers = ["Label", "Time (T)", "VDD Voltage", "VSS Voltage", "Compliance"]
        for i, header in enumerate(headers):
            tk.Label(frame, text=header, font=("Arial", 10, "bold")).grid(row=0, column=i)
        
        def save_as_new():
            new_file_name = save_as_entry.get().strip()
            if new_file_name:
                new_file_path = os.path.join("waveforms", f"{new_file_name}.txt")
                self.save_waveform(waveform_data, new_file_path)

        def update_waveform():
            """Updates the waveform plot."""
            try:
                T_values = [float(entry.get()) for entry in time_entries if entry.get()]
                VDD_values = [entry.get() for entry in vdd_entries]
                VSS_values = [entry.get() for entry in vss_entries]
                
                ax.clear()
                
                # Convert valid numeric entries to float, leave "X" as NaN
                VDD_plot = [float(v) if v.replace('.', '', 1).isdigit() else np.nan for v in VDD_values]
                VSS_plot = [float(v) if v.replace('.', '', 1).isdigit() else np.nan for v in VSS_values]
                
                ax.plot(T_values, VDD_plot, marker="o", linestyle="-", label="VDD Voltage")
                ax.plot(T_values, VSS_plot, marker="s", linestyle="--", label="VSS Voltage")
                
                ax.set_xlabel("Time")
                ax.set_ylabel("Voltage")
                ax.set_title("VDD & VSS Waveform")
                ax.grid()
                ax.legend()
                canvas.draw()

            except ValueError:
                messagebox.showerror("Input Error", "Enter valid numeric values for Time.")

        def save_and_close():
            """Saves waveform data and closes the GUI."""
            nonlocal waveform_data

            VDD_time = []
            VDD_voltage = []
            VSS_time = []
            VSS_voltage = []
            compliance_literals = []
            compliance_data = []

            meas_times = []
            meas_pts = []
            meas_interval = []
            meas_averaging = []
            meas_mode = []

            # Iterate through the entries and filter values correctly
            for time_entry, vdd_entry, vss_entry, label_entry, comp_entry in zip(time_entries, vdd_entries, vss_entries, label_entries, compliance_entries):
                time_val = time_entry.get().strip()  # Clean time input
                vdd_val = vdd_entry.get().strip()  # Clean VDD voltage
                vss_val = vss_entry.get().strip()  # Clean VSS voltage
                label_val = label_entry.get().strip().lower()  # Convert label to lowercase for searching
                comp_val = comp_entry.get().strip().lower()
                trd = measure_duration_entry.get().strip()
                self.trd = trd
                pts_per_meas = num_points_entry.get().strip()
                self.pts_per_meas = pts_per_meas

                if time_val.replace(".", "", 1).isdigit():  # Ensure time is numeric
                    time_val = float(time_val)  # Convert to float

                    # If VDD is NOT "X", store time and voltage for VDD
                    if vdd_val != "X":
                        VDD_time.append(time_val)
                        VDD_voltage.append(float(vdd_val) if vdd_val.replace(".", "", 1).isdigit() else np.nan)

                    # If VSS is NOT "X", store time and voltage for VSS
                    if vss_val != "X":
                        VSS_time.append(time_val)
                        VSS_voltage.append(float(vss_val) if vss_val.replace(".", "", 1).isdigit() else np.nan)

                    # Handle compliance
                    if "comp" in label_val:
                        if comp_val == "1ua":
                            compliance_data.append((time_val, wgc.WGFMU_MEASURE_CURRENT_RANGE_1UA))
                        elif comp_val == "10ua":
                            compliance_data.append((time_val, wgc.WGFMU_MEASURE_CURRENT_RANGE_10UA))
                        elif comp_val == "100ua":
                            compliance_data.append((time_val, wgc.WGFMU_MEASURE_CURRENT_RANGE_100UA))
                        elif comp_val == "1ma":
                            compliance_data.append((time_val, wgc.WGFMU_MEASURE_CURRENT_RANGE_1MA))
                        elif comp_val == "10ma":
                            compliance_data.append((time_val, wgc.WGFMU_MEASURE_CURRENT_RANGE_10MA))
                    
                    compliance_literals.append(0 if comp_val == "0" else comp_val)


                    # Handle measurement events
                    if "meas" in label_val:
                        meas_times.append(time_val)
                        meas_pts.append(pts_per_meas)  # Default is 1
                        meas_interval.append(trd)  # Reading duration
                        meas_averaging.append(trd / 2)  # Averaging period
                        meas_mode.append(wgc.WGFMU_MEASURE_EVENT_DATA_AVERAGED)  # Default averaged mode

                    if "reset" in label_val:  # Check if "reset" is in the label first
                        self.VDD_Reset = [time_val, vdd_val]
                        self.VSS_Reset = [time_val, vss_val]

                    elif "set" in label_val:  # Only check for "set" if "reset" was NOT found
                        self.VDD_Set = [time_val, vdd_val]
                        self.VSS_Set = [time_val, vss_val]
                    
                    if "read" in label_val:
                        self.VDD_rd = [vdd_val]
                        self.VSS_rd = [vss_val]



            # Save the cleaned-up waveform data
            waveform_data = {
                "Labels": [entry.get().strip() for entry in label_entries],
                "VDD Time": VDD_time,
                "VSS Time": VSS_time,
                "VDD Voltage": VDD_voltage,
                "VSS Voltage": VSS_voltage,
                "Compliance Literals": compliance_literals,
                "Compliance Data": compliance_data,
                "Measurement Data": (meas_times, meas_pts, meas_interval, meas_averaging, meas_mode)
            }
            self.waveform_data = waveform_data

            root.quit()
            root.destroy()

        
        for i in range(num_rows):
            label_entry = tk.Entry(frame, width=10)
            label_entry.grid(row=i+1, column=0)
            label_entries.append(label_entry)

            time_entry = tk.Entry(frame, width=10)
            time_entry.grid(row=i+1, column=1)
            time_entries.append(time_entry)

            vdd_entry = tk.Entry(frame, width=10)
            vdd_entry.grid(row=i+1, column=2)
            vdd_entries.append(vdd_entry)

            vss_entry = tk.Entry(frame, width=10)
            vss_entry.grid(row=i+1, column=3)
            vss_entries.append(vss_entry)

            compliance_entry = tk.Entry(frame, width=10)
            compliance_entry.grid(row=i+1, column=4)
            compliance_entries.append(compliance_entry)

            # ✅ Ensure Label Column is always populated
            if i < len(Full_labels):
                label_entry.insert(0, Full_labels[i])

            # ✅ Ensure Other Fields are Populated ONLY if labels is None
            if labels is None:
                if i < len(times):
                    time_entry.insert(0, str(times[i]))
                if i < len(vdd_voltage):
                    vdd_entry.insert(0, str(vdd_voltage[i]))
                if i < len(vss_voltage):
                    vss_entry.insert(0, str(vss_voltage[i]))
                if i < len(compliance):
                    compliance_entry.insert(0, str(compliance[i]))



        # Create a new frame for stacking buttons to the right
        button_frame = tk.Frame(frame)
        button_frame.grid(row=num_rows+1, column=3, rowspan=3, padx=20, pady=5, sticky="n")

        # Update Waveform button (top of the stack)
        tk.Button(button_frame, text="Update Waveform", command=update_waveform).pack(fill="x", pady=5)

        # Save button (below Update Waveform)
        tk.Button(button_frame, text="Save and Run", command=save_and_close).pack(fill="x", pady=5)

        # Save As entry box and Save & Close button in a row
        entry_frame = tk.Frame(button_frame)
        entry_frame.pack(fill="x", pady=5)

        save_as_entry = tk.Entry(entry_frame, width=15)
        save_as_entry.pack(side="left", padx=5)

        tk.Button(entry_frame, text="Save As and Run", command=save_as_new).pack(side="right")


        
        # GUI Fields for additional measurement settings
        tk.Label(frame, text="Measure Duration (s)", font=("Arial", 10, "bold")).grid(row=num_rows+2, column=0)
        measure_duration_entry = tk.Entry(frame, width=10)
        measure_duration_entry.grid(row=num_rows+2, column=1)
        measure_duration_entry.insert(0, "100e-6")

        tk.Label(frame, text="Number of Points per Measure", font=("Arial", 10, "bold")).grid(row=num_rows+3, column=0)
        num_points_entry = tk.Entry(frame, width=10)
        num_points_entry.grid(row=num_rows+3, column=1)
        num_points_entry.insert(0, "1")

        fig, ax = plt.subplots(figsize=(6, 4))
        canvas = FigureCanvasTkAgg(fig, master=root)
        canvas.get_tk_widget().pack(side=tk.RIGHT, expand=True, padx=10, pady=10)

        waveform_data = {}
        root.mainloop()
        return waveform_data

def update_set(self, set_voltage=None, reset_voltage=None):
    """
    Updates the stored 'set' and 'reset' voltages in TestInfo's waveform_data using their stored times.
    Ensures correct alignment between time and voltage values for both VDD and VSS.

    Args:
        set_voltage (float, optional): New voltage value for 'set' condition.
        reset_voltage (float, optional): New voltage value for 'reset' condition.
    """
    vdd_times = self.waveform_data["VDD Time"]
    vss_times = self.waveform_data["VSS Time"]
    vdd_voltages = self.waveform_data["VDD Voltage"]
    vss_voltages = self.waveform_data["VSS Voltage"]

    # 🔹 Update RESET voltage if specified
    if reset_voltage is not None:
        vdd_reset_time, _ = self.VDD_Reset  # Extract stored reset time
        vss_reset_time, _ = self.VSS_Reset  

        if vdd_reset_time in vdd_times:
            idx = vdd_times.index(vdd_reset_time)
            print(f"🔄 Updating VDD Reset Voltage at {vdd_reset_time}s: {vdd_voltages[idx]} → {reset_voltage}")
            vdd_voltages[idx] = reset_voltage
            self.VDD_Reset[1] = reset_voltage  # Update stored value

        if vss_reset_time in vss_times:
            idx = vss_times.index(vss_reset_time)
            print(f"🔄 Updating VSS Reset Voltage at {vss_reset_time}s: {vss_voltages[idx]} → {reset_voltage}")
            vss_voltages[idx] = reset_voltage
            self.VSS_Reset[1] = reset_voltage

    # 🔹 Update SET voltage if specified
    if set_voltage is not None:
        vdd_set_time, _ = self.VDD_Set  # Extract stored set time
        vss_set_time, _ = self.VSS_Set  

        if vdd_set_time in vdd_times:
            idx = vdd_times.index(vdd_set_time)
            print(f"🔄 Updating VDD Set Voltage at {vdd_set_time}s: {vdd_voltages[idx]} → {set_voltage}")
            vdd_voltages[idx] = set_voltage
            self.VDD_Set[1] = set_voltage

        if vss_set_time in vss_times:
            idx = vss_times.index(vss_set_time)
            print(f"🔄 Updating VSS Set Voltage at {vss_set_time}s: {vss_voltages[idx]} → {set_voltage}")
            vss_voltages[idx] = set_voltage
            self.VSS_Set[1] = set_voltage

    print("✅ Waveform data updated successfully.")
