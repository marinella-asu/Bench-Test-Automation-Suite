import time
import tkinter as tk
from tkinter import simpledialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import wgfmu_consts as wgc
import os
import math
import csv


class TestInfo:
    def __init__(self, parameters=None):
        """
        Initializes TestInfo with parameters.
        Args:
            parameters (dict): Dictionary of parameters with their default values.
        """
        self.parameters = parameters or {}
        self.waveform_data = {}

    def save_and_close(self):
        global waveform_data_path  # Use the global path for saving
        """Saves waveform data and closes the GUI."""
        VDD_time, VDD_voltage = [], []
        VSS_time, VSS_voltage = [], []
        compliance_data = []

        meas_times, meas_pts, meas_interval, meas_averaging, meas_mode = [], [], [], [], []
        trd = float(measure_duration_entry.get().strip()) if measure_duration_entry.get().strip() else 100e-6
        num_pts_per_measure = int(num_points_entry.get().strip()) if num_points_entry.get().strip() else 1
        
        rows_to_save = []
    
        for time_entry, vdd_entry, vss_entry, label_entry, comp_entry in zip(
            time_entries, vdd_entries, vss_entries, label_entries, compliance_entries
        ):
            time_val = time_entry.get().strip()
            vdd_val = vdd_entry.get().strip()
            vss_val = vss_entry.get().strip()
            label_val = label_entry.get().strip().lower()
            comp_val = comp_entry.get().strip().lower()
            
            rows_to_save.append([label_val, time_val, vdd_val, vss_val, comp_val, ""])
            
            if time_val.replace(".", "", 1).isdigit():
                time_val = float(time_val)

                if vdd_val != "X":
                    VDD_time.append(time_val)
                    VDD_voltage.append(float(vdd_val) if vdd_val.replace(".", "", 1).isdigit() else np.nan)
                if vss_val != "X":
                    VSS_time.append(time_val)
                    VSS_voltage.append(float(vss_val) if vss_val.replace(".", "", 1).isdigit() else np.nan)

                if "comp" in label_val:
                    compliance_lookup = {
                        "1ua": wgc.WGFMU_MEASURE_CURRENT_RANGE_1UA,
                        "10ua": wgc.WGFMU_MEASURE_CURRENT_RANGE_10UA,
                        "100ua": wgc.WGFMU_MEASURE_CURRENT_RANGE_100UA,
                        "1ma": wgc.WGFMU_MEASURE_CURRENT_RANGE_1MA,
                        "10ma": wgc.WGFMU_MEASURE_CURRENT_RANGE_10MA,
                    }
                    if comp_val in compliance_lookup:
                        compliance_data.append((time_val, compliance_lookup[comp_val]))

                if "meas" in label_val:
                    meas_times.append(time_val)
                    meas_pts.append(num_pts_per_measure)
                    meas_interval.append(trd)
                    meas_averaging.append(trd / 2)
                    meas_mode.append(1)

        waveform_data = {
            "Labels": [entry.get().strip() for entry in label_entries],
            "VDD Time": VDD_time,
            "VSS Time": VSS_time,
            "VDD Voltage": VDD_voltage,
            "VSS Voltage": VSS_voltage,
            "Compliance": compliance_data,
            "Measurement Data": (meas_times, meas_pts, meas_interval, meas_averaging, meas_mode)
        }

        self.waveform_data = waveform_data
        
        # Write CSV with 6 columns to waveform_data_path
        try:
            with open(waveform_data_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerows(rows_to_save)
        except Exception as e:
            print(f"Error saving waveform CSV: {e}")
        root.quit()
        root.destroy()

    def launch_waveform_editor(self, labels=None, times = None, VDD_Values = None, VSS_Values = None, Comp = None):
        global root, label_entries, time_entries, vdd_entries, vss_entries, compliance_entries
        global measure_duration_entry, num_points_entry

        root = tk.Tk()
        root.title("Waveform Editor")
        root.geometry("1200x700")

        num_rows = len(labels) if labels else 11
        label_entries, time_entries, vdd_entries, vss_entries, compliance_entries = [], [], [], [], []

        frame = tk.Frame(root)
        frame.pack(side=tk.LEFT, padx=10, pady=10)

        headers = ["Label", "Time (T)", "VDD Voltage", "VSS Voltage", "Compliance"]
        for i, header in enumerate(headers):
            tk.Label(frame, text=header, font=("Arial", 10, "bold")).grid(row=0, column=i)

        for i in range(num_rows):
            label_entry = tk.Entry(frame, width=10)
            label_entry.grid(row=i + 1, column=0)
            label_entry.insert(0, labels[i] if labels and i < len(labels) else "")
            label_entries.append(label_entry)

            time_entry = tk.Entry(frame, width=10)
            time_entry.grid(row=i + 1, column=1)
            time_entry.insert(0, times[i] if times and i < len(times) else "")
            time_entries.append(time_entry)

            vdd_entry = tk.Entry(frame, width=10)
            vdd_entry.grid(row=i + 1, column=2)
            vdd_entry.insert(0, VDD_Values[i] if VDD_Values and i < len(VDD_Values) else "")
            vdd_entries.append(vdd_entry)

            vss_entry = tk.Entry(frame, width=10)
            vss_entry.grid(row=i + 1, column=3)
            vss_entry.insert(0, VSS_Values[i] if VSS_Values and i < len(VSS_Values) else "")
            vss_entries.append(vss_entry)

            compliance_entry = tk.Entry(frame, width=10)
            compliance_entry.grid(row=i + 1, column=4)
            compliance_entry.insert(0, Comp[i] if Comp and i < len(Comp) else "")
            compliance_entries.append(compliance_entry)

        # Extra input fields for measurement configuration
        tk.Label(frame, text="Measure Duration (s)", font=("Arial", 10, "bold")).grid(row=num_rows + 2, column=0, pady=5)
        measure_duration_entry = tk.Entry(frame, width=10)
        measure_duration_entry.grid(row=num_rows + 2, column=1)
        measure_duration_entry.insert(0, "100e-6")

        tk.Label(frame, text="Points per Measure", font=("Arial", 10, "bold")).grid(row=num_rows + 3, column=0, pady=5)
        num_points_entry = tk.Entry(frame, width=10)
        num_points_entry.grid(row=num_rows + 3, column=1)
        num_points_entry.insert(0, "1")

        # Buttons
        tk.Button(frame, text="Update Waveform", command=self.update_waveform).grid(row=num_rows + 4, column=0, columnspan=2, pady=10)
        tk.Button(frame, text="Save and Close", command=self.save_and_close).grid(row=num_rows + 4, column=3, columnspan=2, pady=10)

        # Matplotlib plot
        fig, ax = plt.subplots(figsize=(6, 4))
        self.ax = ax
        canvas = FigureCanvasTkAgg(fig, master=root)
        canvas.get_tk_widget().pack(side=tk.RIGHT, expand=True, padx=10, pady=10)
        self.canvas = canvas

        root.mainloop()
        return self.waveform_data
    

    def update_waveform(self):
        
        def is_number(s: str) -> bool:
            try:
                float(s)
                return True
            except ValueError:
                return False

        def forward_fill(values_raw):
            """
            Convert a list of raw strings to floats, treating 'x' (or blank) as
            'same as last good value'.  The series remains the SAME LENGTH.
            """
            filled = []
            last_val = np.nan          # start unknown

            for v in values_raw:
                v = v.strip()
                if v.lower() == "x" or not is_number(v):
                    # keep previous value
                    filled.append(last_val)
                else:
                    last_val = float(v)
                    filled.append(last_val)

            # If the very first entries were 'x', back‑fill them with the
            # first real number so the line starts solid.
            if math.isnan(filled[0]):
                try:
                    first_real = next(val for val in filled if not math.isnan(val))
                    filled = [first_real if math.isnan(val) else val for val in filled]
                except StopIteration:
                    pass   # all NaN – leave as‑is

            return filled
            
            
        """Updates the waveform plot."""
        try:
            # 1) pull raw strings
            T_raw   = [e.get().strip() for e in time_entries]
            VDD_raw = [e.get().strip() for e in vdd_entries]
            VSS_raw = [e.get().strip() for e in vss_entries]

            # 2) numeric time axis (assume every Time box has a value)
            T_values = [float(t) for t in T_raw]

            # 3) forward‑fill the voltage lists
            VDD_plot = forward_fill(VDD_raw)
            VSS_plot = forward_fill(VSS_raw)

            # 4) draw (use a step style so the change appears instantaneous)
            self.ax.clear()
            self.ax.plot(T_values, VDD_plot, marker="o", linestyle="-",
                          label="VDD Voltage")
            self.ax.plot(T_values, VSS_plot, marker="s", linestyle="--",
                         label="VSS Voltage")

            self.ax.set_xlabel("Time")
            self.ax.set_ylabel("Voltage")
            self.ax.set_title("VDD & VSS Waveform")
            self.ax.grid(True)
            self.ax.legend()
            self.canvas.draw()

        except ValueError:
            messagebox.showerror("Input Error", "Make sure all Time values are numeric.")


    def validate_and_prompt(self, timeout=300):
        global waveform_data_path
        """
        Validates parameters and prompts the user to fill missing ones via a GUI.
        If the GUI stays open for more than the timeout, the program exits.

        Args:
            timeout (int): Time in seconds before the program exits if parameters are not filled.

        Raises:
            SystemExit: If required parameters are not filled within the timeout.
        """
        missing_params = {k: v 
                          for k, v in self.parameters.items()
                          if v in [None, "ask"] and k != "Waveform Editor"}

                # --- Launch waveform editor if requested ---
        if self.parameters.get("Waveform Editor", "").lower() == "ask":
            format_name = self.parameters.get("Waveform Format", None)
            waveform_data_name = self.parameters.get("Waveform", None)
            labels = []
            script_dir = os.path.dirname(os.path.abspath(__file__))
            while not script_dir.endswith("Bench-Test-Automation-Suite-main"):
                script_dir = os.path.dirname(script_dir)  # Move up one level

            # Ensure the data is stored inside "Bench_Test_Automation_Suite/Data"
            waveform_data_path = os.path.join(script_dir, "Waveforms", f"{waveform_data_name}.txt")
            
            # print(waveform_data_path)
            if os.path.exists(waveform_data_path):
                with open(waveform_data_path, "r") as f:
                    VDD_data = [line.strip() for line in f.readlines()]
                print(f"✅ Loaded waveform from {waveform_data_path}")

            labels = []
            times = []
            vdd_values = []
            vss_values = []
            comps = []

            for line in VDD_data:
                parts = line.split(",")
                label = parts[0]
                time = float(parts[1])
                vdd_val= float(parts[2])
                vss_val = float(parts[3])
                comp = parts[4] if len(parts) > 4 else ""

                labels.append(label)
                times.append(time)
                vdd_values.append(vdd_val)
                vss_values.append(vss_val)
                comps.append(comp)



            # # Example output
            # print("Labels:", labels)
            # print("Times:", times)
            # print("VDD:", vdd_values)
            # print("VSS:", vss_values)
            # print("Compliance:", comps)


            # if format_name:
            #     format_path = os.path.join("Waveforms", "Formats", f"{format_name}.txt")
            #     waveform_data_path = os.path.join("Waveforms", f"{waveform_data_name}.txt")
            #     if os.path.exists(format_path):
            #         with open(format_path, "r") as f:
            #             labels = [line.strip() for line in f.readlines()]
            #         print(f"✅ Loaded waveform format from {format_path}")
            #     if os.path.exists(waveform_data_path):
            #         with open(waveform_data_path, "r") as f:
            #             VDD_data = [line.strip() for line in f.readlines()]
            #         print(f"✅ Loaded waveform format from {waveform_data_path}")
            #     else:
            #         print(f"⚠️ Format file not found: {format_path}")
            
            print("📈 Launching waveform editor...")
            self.launch_waveform_editor( labels, times, vdd_values, vss_values, comps)


        if not missing_params:
            print("All parameters are set. Proceeding with the test.")
            return  # All parameters are already defined

        print("Some parameters are missing. Launching GUI...")

        def on_submit():
            """Collects user input from the GUI and updates parameters."""
            for key, entry in entry_widgets.items():
                value = entry.get().strip()
                if value:
                    self.parameters[key] = value
            root.quit()  # Close the GUI loop

        def on_timeout():
            """Handles timeout for the GUI and exits the program."""
            print("Timeout reached. Exiting due to missing parameters.")
            root.quit()
            exit()
        
        # Create the GUI
        root = tk.Tk()
        root.title("Parameter Input")
        root.geometry("400x300")

        # Label for instructions
        tk.Label(root, text="Please fill in the required parameters:", font=("Arial", 12)).pack(pady=10)

        # Create entry widgets for each missing parameter
        entry_widgets = {}
        for param in missing_params:
            frame = tk.Frame(root)
            frame.pack(pady=5, fill="x", padx=10)
            tk.Label(frame, text=f"{param}:", width=20, anchor="w").pack(side="left")
            entry = tk.Entry(frame)
            entry.pack(side="right", fill="x", expand=True)
            entry_widgets[param] = entry

        # Submit button (Now properly positioned)
        submit_button = tk.Button(root, text="Submit", command=on_submit)
        submit_button.pack(pady=20)

        # Start a timer for timeout
        timer_id = root.after(timeout * 1000, on_timeout)

        # Run the GUI main loop
        root.mainloop()

        # Cancel the timer if the GUI closes properly
        root.after_cancel(timer_id)

        # Check if there are still missing parameters
        remaining_missing_params = {k: v 
                                  for k, v in self.parameters.items()
                                  if v in [None, "ask"] and k != "Waveform Editor"}
        if remaining_missing_params:
            print(f"Missing parameters: {remaining_missing_params}")
            exit(1)  # Exit if parameters are still missing

        print("All parameters are set. Proceeding with the test.")

        
