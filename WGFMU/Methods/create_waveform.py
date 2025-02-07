import ctypes as ct  # Import C types for handling API calls
import time  # Import time module for performance tracking
import wgfmu_consts as wgc  # Import constants for WGFMU operations

def generate_wgfmu_waveform(self, channel_list, drive_profile, range_settings=(), measurement_settings=(),
                            num_repetitions=1, include_in_sequence=True, waveform_label=""):
    """
    Generates a WGFMU waveform pattern and optionally adds it to a sequence.

    Args:
        channel_list (int or list): WGFMU channel(s) to configure.
        drive_profile (tuple): (time_values, voltage_values), both NumPy arrays.
        range_settings (tuple, optional): (time_values, range_values), NumPy array and list.
        measurement_settings (tuple, optional): (time_values, num_samples, interval, avg_time, mode).
        num_repetitions (int, optional): Number of times to repeat the waveform. Defaults to 1.
        include_in_sequence (bool, optional): Whether to add waveform to execution sequence. Defaults to True.
        waveform_label (str, optional): Label for waveform naming. Defaults to "".

    Returns:
        str: Name of the generated waveform pattern.
    """
    # If a single integer channel is passed, convert it into a list for consistency
    if isinstance(channel_list, int):
        channel_list = [channel_list]

    # Generate a unique timestamp to avoid duplicate pattern names
    unique_timestamp = time.perf_counter()

    # Generate unique vector names for each channel
    pattern_names = [self.cstr(f"ch{channel}_{waveform_label}_{unique_timestamp}") for channel in channel_list]

    # Iterate through each channel in the list
    for idx, channel_id in enumerate(channel_list):
        pattern_name = pattern_names[idx]

        # Create waveform pattern in WGFMU
        self.wg.WGFMU_createPattern(pattern_name, self.cf(0))

        # Extract time and voltage data for the waveform
        time_values, voltage_values = drive_profile

        # Iterate through each time step and set voltage values
        for step_idx in range(len(time_values)):
            time_point = self.cf(time_values[step_idx])  # Convert to C-type float
            voltage_level = self.cf(voltage_values[step_idx])  # Convert to C-type float

            # Apply the vector settings to WGFMU
            self.wg.WGFMU_setVector(pattern_name, time_point, voltage_level)

        # Add range settings if provided
        if len(range_settings) > 0:
            range_times, range_values = range_settings

            for range_idx in range(len(range_times)):
                range_time = self.cf(range_times[range_idx])  # Convert to C-type float
                range_value = range_values[range_idx]  # Range setting value
                range_event_label = self.cstr(f"ch{channel_id}_range{range_idx}_{unique_timestamp}")

                # Apply range setting at the specified time
                self.wg.WGFMU_setRangeEvent(pattern_name, range_event_label, range_time, range_value)

        # Add measurement settings if provided
        if len(measurement_settings) > 0:
            measure_times, sample_counts, time_intervals, avg_times, modes = measurement_settings

            for measure_idx in range(len(measure_times)):
                measure_time = self.cf(measure_times[measure_idx])  # Convert to C-type float
                sample_count = int(sample_counts[measure_idx])  # Convert to integer
                time_interval = self.cf(time_intervals[measure_idx])  # Convert to C-type float
                avg_time = self.cf(avg_times[measure_idx])  # Convert to C-type float
                measure_mode = int(modes[measure_idx])  # Convert to integer
                measure_event_label = self.cstr(f"ch{channel_id}_meas{measure_idx}_{unique_timestamp}")

                # Set measurement event for the pattern
                self.wg.WGFMU_setMeasureEvent(pattern_name, measure_event_label, measure_time,
                                              sample_count, time_interval, avg_time, measure_mode)

        # Add waveform pattern to sequence if specified
        if include_in_sequence:
            self.wg.WGFMU_addSequence(channel_id, pattern_name, self.cf(num_repetitions))

        return pattern_name  # Return the generated pattern name
