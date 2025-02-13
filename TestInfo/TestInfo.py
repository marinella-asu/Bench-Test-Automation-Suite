import os
import tkinter as tk
from tkinter import messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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
        missing_params = {k: v for k, v in self.parameters.items() if v in [None, "ask"] and k not in ["VDD Waveform", "VDD Waveform Format", "VSS Waveform", "VSS Waveform Format"]}

        # List of waveform-related keys to exclude
        waveform_keys = {"VDD Waveform", "VDD Waveform Format", "VSS Waveform", "VSS Waveform Format"}

        # Dynamically assign parameters as attributes
        for key, value in self.parameters.items():
            if key not in waveform_keys:  # Exclude waveform-related parameters
                safe_key = key.replace(" ", "_")  # Convert spaces to underscores
                setattr(self, safe_key, value)  # Assign as attribute


        if missing_params:
            self.prompt_user_for_parameters(missing_params, timeout)

        # Handle waveform input AFTER parameter validation
        if "VDD Waveform" in self.parameters:
            self.handle_VDD_waveform()
        if "VSS Waveform" in self.parameters:
            self.handle_VSS_waveform()

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
        waveform_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Waveforms", "VDD_Waveforms")
        format_folder = os.path.join(waveform_folder, "VDD_Formats")
        os.makedirs(waveform_folder, exist_ok=True)
        os.makedirs(format_folder, exist_ok=True)

        waveform_param = self.parameters["VDD Waveform"]
        waveform_format = self.parameters.get("VDD Waveform Format", None)
        user_name = self.parameters.get("Name", "User").replace(" ", "_")

        # Load waveform format if specified
        format_labels = None
        if waveform_format:
            format_path = os.path.join(format_folder, f"{waveform_format}.txt")
            if os.path.exists(format_path):
                format_labels = self.load_waveform_format(format_path)
                print(f"✅ Loaded waveform format: {waveform_format}")
            else:
                print(f"⚠️ Waveform format {waveform_format} not found.")

        # If user requests a new waveform
        if waveform_param == "ask":
            print("Launching waveform editor...")
            waveform_data = self.launch_waveform_editor(format_labels)

            # Determine next available waveform number
            existing_waveforms = [f for f in os.listdir(waveform_folder) if f.startswith(user_name)]
            next_waveform_number = len(existing_waveforms) + 1
            waveform_filename = f"{user_name}_{waveform_format}_{next_waveform_number}.txt" if waveform_format else f"{user_name}_{next_waveform_number}.txt"

            waveform_path = os.path.join(waveform_folder, waveform_filename)
            self.save_waveform(waveform_data, waveform_path)
            self.parameters["VDD Waveform"] = waveform_filename
            print(f"✅ Waveform saved as {waveform_filename}")

        else:
            waveform_path = os.path.join(waveform_folder, f"{waveform_param}.txt")
            if not os.path.exists(waveform_path):
                print(f"⚠️ Waveform {waveform_param} not found. Creating a new one.")
                waveform_data = self.launch_waveform_editor(format_labels)
                self.save_waveform(waveform_data, waveform_path)

        # Load waveform data
        T_values, V_values = self.load_waveform(waveform_path)
        self.parameters["VDD Waveform Data"] = {"Time": T_values, "Voltage": V_values}
        print(f"✅ Waveform {self.parameters['VDD Waveform']} loaded with {len(T_values)} points.")

    def handle_VSS_waveform(self):
        """Handles waveform input, including waveform formats."""
        waveform_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Waveforms", "VSS_Waveforms")
        format_folder = os.path.join(waveform_folder, "VSS_Formats")
        os.makedirs(waveform_folder, exist_ok=True)
        os.makedirs(format_folder, exist_ok=True)

        waveform_param = self.parameters["VSS Waveform"]
        waveform_format = self.parameters.get("VSS Waveform Format", None)
        user_name = self.parameters.get("Name", "User").replace(" ", "_")

        # Load waveform format if specified
        format_labels = None
        if waveform_format:
            format_path = os.path.join(format_folder, f"{waveform_format}.txt")
            if os.path.exists(format_path):
                format_labels = self.load_waveform_format(format_path)
                print(f"✅ Loaded waveform format: {waveform_format}")
            else:
                print(f"⚠️ Waveform format {waveform_format} not found.")

        # If user requests a new waveform
        if waveform_param == "ask":
            print("Launching waveform editor...")
            waveform_data = self.launch_waveform_editor(format_labels)

            # Determine next available waveform number
            existing_waveforms = [f for f in os.listdir(waveform_folder) if f.startswith(user_name)]
            next_waveform_number = len(existing_waveforms) + 1
            waveform_filename = f"{user_name}_{waveform_format}_{next_waveform_number}.txt" if waveform_format else f"{user_name}_{next_waveform_number}.txt"

            waveform_path = os.path.join(waveform_folder, waveform_filename)
            self.save_waveform(waveform_data, waveform_path)
            self.parameters["VSS Waveform"] = waveform_filename
            print(f"✅ Waveform saved as {waveform_filename}")

        else:
            waveform_path = os.path.join(waveform_folder, f"{waveform_param}.txt")
            if not os.path.exists(waveform_path):
                print(f"⚠️ Waveform {waveform_param} not found. Creating a new one.")
                waveform_data = self.launch_waveform_editor(format_labels)
                self.save_waveform(waveform_data, waveform_path)

        # Load waveform data
        T_values, V_values = self.load_waveform(waveform_path)
        self.parameters["VSS Waveform Data"] = {"Time": T_values, "Voltage": V_values}
        print(f"✅ Waveform {self.parameters['VSS Waveform']} loaded with {len(T_values)} points.")

    def load_waveform_format(self, format_path):
        """Loads the waveform format file and returns the list of labels."""
        with open(format_path, "r") as f:
            labels = [line.strip() for line in f.readlines()]
        return labels

    def load_waveform(self, file_path):
        """Loads waveform data from a text file into NumPy arrays."""
        if not os.path.exists(file_path):
            print(f"⚠️ Waveform file {file_path} not found. Returning empty arrays.")
            return np.array([]), np.array([])

        try:
            data = np.loadtxt(file_path, delimiter="\t")
            if data.shape[1] != 2:
                raise ValueError("Invalid waveform format. Expected two columns: Time and Voltage.")
            return data[:, 0], data[:, 1]  # Extract Time and Voltage columns

        except Exception as e:
            print(f"⚠️ Error loading waveform file: {e}")
            return np.array([]), np.array([])

    def save_waveform(self, waveform_data, file_path):
            """Saves waveform data to a text file."""
            np.savetxt(file_path, np.column_stack((waveform_data["Time"], waveform_data["Voltage"])), delimiter="\t")
            print(f"Waveform saved to {file_path}")

    def launch_waveform_editor(self, labels=None):
        """Opens the waveform editor GUI with an optional format."""
        root = tk.Tk()
        root.title("Waveform Editor")
        root.geometry("1000x500")

        # Determine the number of rows based on labels
        num_rows = len(labels) if labels else 11
        label_entries, time_entries, voltage_entries = [], [], []

        def update_waveform():
            """Updates the waveform plot."""
            try:
                T_values = [float(entry.get()) for entry in time_entries if entry.get()]
                V_values = [float(entry.get()) for entry in voltage_entries if entry.get()]

                if len(T_values) != len(V_values):
                    messagebox.showerror("Input Error", "Mismatch in number of time and voltage values")
                    return

                ax.clear()
                ax.plot(T_values, V_values, marker="o", linestyle="-")
                ax.set_xlabel("Time")
                ax.set_ylabel("Voltage")
                ax.set_title(f"Voltage Waveform")
                ax.grid()
                canvas.draw()

            except ValueError:
                messagebox.showerror("Input Error", "Enter valid numeric values.")

        def save_and_close():
            """Saves waveform data and closes the GUI."""
            nonlocal waveform_data
            waveform_data = {
                "Labels": [entry.get().strip() for entry in label_entries],
                "Time": [float(entry.get()) for entry in time_entries if entry.get()],
                "Voltage": [float(entry.get()) for entry in voltage_entries if entry.get()]
            }
            root.quit()
            root.destroy()

        frame = tk.Frame(root)
        frame.pack(side=tk.LEFT, padx=10, pady=10)

        tk.Label(frame, text="Label").grid(row=0, column=0)
        tk.Label(frame, text="Time (T)").grid(row=0, column=1)
        tk.Label(frame, text="Voltage (V)").grid(row=0, column=2)

        
        for i in range(num_rows):
            label_entry = tk.Entry(frame, width=10)
            label_entry.grid(row=i+1, column=0)
            label_entry.insert(0, labels[i] if labels and i < len(labels) else "")
            label_entries.append(label_entry)

            time_entry = tk.Entry(frame, width=10)
            time_entry.grid(row=i+1, column=1)
            time_entries.append(time_entry)

            voltage_entry = tk.Entry(frame, width=10)
            voltage_entry.grid(row=i+1, column=2)
            voltage_entries.append(voltage_entry)

        tk.Button(frame, text="Update Waveform", command=update_waveform).grid(row=num_rows+1, column=0, columnspan=2)
        tk.Button(frame, text="Save and Close", command=save_and_close).grid(row=num_rows+1, column=2, columnspan=2)

        fig, ax = plt.subplots(figsize=(6, 4))
        canvas = FigureCanvasTkAgg(fig, master=root)
        canvas.get_tk_widget().pack(side=tk.RIGHT, expand=True, padx=10, pady=10)

        waveform_data = {}
        root.mainloop()
        return waveform_data
