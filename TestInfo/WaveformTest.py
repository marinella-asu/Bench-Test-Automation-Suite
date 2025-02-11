import tkinter as tk
from tkinter import messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class WaveformGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Waveform Editor")
        self.root.geometry("900x500")  # Increase window size
        self.waveform_updated = False  # Track if "Update Waveform" was clicked

        # Time and Voltage Inputs
        self.time_entries = []
        self.voltage_entries = []

        # Frame for Input Fields
        input_frame = tk.Frame(root)
        input_frame.pack(side=tk.LEFT, padx=10, pady=10)

        tk.Label(input_frame, text="Time (T)", font=("Arial", 12)).grid(row=0, column=1, padx=5, pady=5)
        tk.Label(input_frame, text="Voltage (V)", font=("Arial", 12)).grid(row=0, column=2, padx=5, pady=5)

        for i in range(11):
            tk.Label(input_frame, text=f"T{i}", font=("Arial", 10)).grid(row=i+1, column=0, padx=5, pady=2)
            time_entry = tk.Entry(input_frame, width=10, font=("Arial", 10))
            time_entry.grid(row=i+1, column=1, padx=5, pady=2)
            self.time_entries.append(time_entry)

            voltage_entry = tk.Entry(input_frame, width=10, font=("Arial", 10))
            voltage_entry.grid(row=i+1, column=2, padx=5, pady=2)
            self.voltage_entries.append(voltage_entry)

        # Buttons
        button_frame = tk.Frame(root)
        button_frame.pack(side=tk.LEFT, padx=10, pady=10)

        self.update_button = tk.Button(button_frame, text="Update Waveform", font=("Arial", 12), command=self.update_waveform)
        self.update_button.pack(pady=5, fill=tk.X)

        self.run_button = tk.Button(button_frame, text="Run", font=("Arial", 12), command=self.run_program)
        self.run_button.pack(pady=5, fill=tk.X)

        # Matplotlib Figure
        self.figure, self.ax = plt.subplots(figsize=(6, 4))  # Increase figure size
        self.canvas = FigureCanvasTkAgg(self.figure, master=root)
        self.canvas.get_tk_widget().pack(side=tk.RIGHT, expand=True, padx=10, pady=10)

    def update_waveform(self):
        """ Updates the waveform plot but does NOT save or output data. """
        try:
            T_values = [float(entry.get()) for entry in self.time_entries if entry.get()]
            V_values = [float(entry.get()) for entry in self.voltage_entries if entry.get()]

            if len(T_values) != len(V_values):
                messagebox.showerror("Input Error", "Mismatch in number of time and voltage values")
                return

            # Sort by time in case inputs are not in order
            T_values, V_values = zip(*sorted(zip(T_values, V_values)))

            # Clear the previous plot
            self.ax.clear()
            self.ax.plot(T_values, V_values, marker="o", linestyle="-", label="Waveform")
            self.ax.set_xlabel("Time")
            self.ax.set_ylabel("Voltage")
            self.ax.set_title("User-Defined Waveform")
            self.ax.legend()
            self.ax.grid()

            # Redraw canvas
            self.canvas.draw()

            # Mark waveform as updated
            self.waveform_updated = True

        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numeric values.")

    def run_program(self):
        """ Ensures the waveform is updated before running the program. """
        if not self.waveform_updated:
            response = messagebox.askyesno("Confirm", "Don't you want to see what it looks like first?")
            if not response:
                return  # User chose not to proceed

        # If user confirms or waveform is updated, output the data and close the window
        T_values = [float(entry.get()) for entry in self.time_entries if entry.get()]
        V_values = [float(entry.get()) for entry in self.voltage_entries if entry.get()]

        # Ensure valid data
        if len(T_values) != len(V_values):
            messagebox.showerror("Input Error", "Mismatch in number of time and voltage values")
            return

        # Sort by time
        T_values, V_values = zip(*sorted(zip(T_values, V_values)))

        # Print the arrays (You can replace this with saving or passing to another function)
        print("T_values:", list(T_values))
        print("V_values:", list(V_values))

        # Close the GUI window
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = WaveformGUI(root)
    root.mainloop()
