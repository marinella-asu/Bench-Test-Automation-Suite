import time
import tkinter as tk
from tkinter import simpledialog, messagebox


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
        If the GUI stays open for more than the timeout, the program exits.

        Args:
            timeout (int): Time in seconds before the program exits if parameters are not filled.

        Raises:
            SystemExit: If required parameters are not filled within the timeout.
        """
        missing_params = {k: v for k, v in self.parameters.items() if v in [None, "ask"]}

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
            exit(1)

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
        remaining_missing_params = [k for k, v in self.parameters.items() if v in [None, "ask"]]
        if remaining_missing_params:
            print(f"Missing parameters: {remaining_missing_params}")
            exit(1)  # Exit if parameters are still missing

        print("All parameters are set. Proceeding with the test.")
