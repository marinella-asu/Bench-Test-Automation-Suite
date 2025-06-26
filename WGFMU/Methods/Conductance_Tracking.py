import numpy as np
import matplotlib.pyplot as plt
import datetime

def Conductance_Tracking(self, 
                                     b1500=None, 
                                     param_name=None,
                                     v_start=.3,
                                     v_max=3.0,
                                     v_step=0.1,
                                     pulses_per_voltage=100,
                                     derivative_interval=10,
                                     v_rd=0.1,
                                     ranging_rd=6002,
                                     read_waveform="Evan_Reram_4",
                                     program_waveform="Evan_Reram_4",
                                     **overrides):

    now = datetime.datetime.now()
    date_time = now.strftime("%Y-%m-%d_%H-%M-%S")

    # Collect all parameters in the same way as your original
    final_params = {
        "v_start": v_start,
        "v_max": v_max,
        "v_step": v_step,
        "pulses_per_voltage": pulses_per_voltage,
        "derivative_interval": derivative_interval,
        "v_rd": v_rd,
        "ranging_rd": ranging_rd,
        "read_waveform": read_waveform,
        "program_waveform": program_waveform
    }

    if b1500 and param_name:
        param_block = dict(b1500.parameters.get(param_name, {}))
        param_block.update(overrides)
        for key, value in param_block.items():
            setattr(b1500, f"{key}_{param_name}", value)
        final_params.update(param_block)
    else:
        final_params.update(overrides)

    # Extract final values
    v_start = final_params["v_start"]
    v_max = final_params["v_max"]
    v_step = final_params["v_step"]
    pulses_per_voltage = final_params["pulses_per_voltage"]
    derivative_interval = final_params["derivative_interval"]
    v_rd = final_params["v_rd"]
    ranging_rd = final_params["ranging_rd"]
    read_waveform = final_params["read_waveform"]
    program_waveform = final_params["program_waveform"]

    # Outputs to store
    all_voltages = []
    before_conductance = []
    after_conductance = []
    all_conductances = []
    all_derivatives = []

    g_after = .002 #initial Value for better conductance ranging
    v = v_start
    while v <= v_max:
        print(f"\n--- Voltage: {v:.2f} V ---")

        # Read initial conductance
        g_before = np.mean(self.rd_pulses_Resalat(b1500, alternate_waveform=read_waveform, v_rd=v_rd, ranging_rd=self.get_wgfmu_range_for_gtarget(g_after))[2])
        conductances = []

        for i in range(pulses_per_voltage):
            # Program a pulse
            self.wg.WGFMU_clear()
            self.create_waveform(b1500, alternate_waveform=program_waveform,
                                 OverrideValue=[("program", v), ("comp", self.get_wgfmu_range_for_gtarget(g_before))])
            self.wgfmu_run([b1500.test_info.ch_vdd, b1500.test_info.ch_vss], open_first=True, close_after=True)

            # Read result
            times, vals = self.read_results(b1500.test_info.ch_vdd)
            g_cur = vals[-1] / v_rd
            conductances.append(g_cur)

        g_after = conductances[-1]
        derivs = np.gradient(conductances, derivative_interval)

        before_conductance.append(g_before)
        after_conductance.append(g_after)
        all_voltages.append(v)
        all_conductances.append(conductances)
        all_derivatives.append(derivs)

        # Plot conductance
        plt.figure()
        plt.plot(range(pulses_per_voltage), conductances, label=f"{v:.2f}V")
        plt.xlabel("Pulse Number")
        plt.ylabel("Conductance (S)")
        plt.title(f"Conductance over Pulses @ {v:.2f}V")
        plt.grid(True)
        plt.tight_layout()
        plt.show()

        # Plot derivative
        plt.figure()
        plt.plot(range(pulses_per_voltage), derivs, label=f"{v:.2f}V Derivative")
        plt.xlabel("Pulse Number")
        plt.ylabel("dG/dPulse")
        plt.title(f"Conductance Derivative over Pulses @ {v:.2f}V")
        plt.grid(True)
        plt.tight_layout()
        plt.show()

        v += v_step

    # Compute drops
    drops = np.array(before_conductance) - np.array(after_conductance)

    # Final output summary
    for i, v in enumerate(all_voltages):
        print(f"Voltage: {v:.2f} V")
        print(f"  Start Conductance: {before_conductance[i]*1e6:.2f} uS")
        print(f"  End Conductance:   {after_conductance[i]*1e6:.2f} uS")
        print(f"  Drop:              {drops[i]*1e6:.2f} uS")
        print("-" * 40)

    return {
        "voltages": all_voltages,
        "g_before": before_conductance,
        "g_after": after_conductance,
        "drops": drops,
        "all_conductances": all_conductances,
        "all_derivatives": all_derivatives
    }

def get_wgfmu_range_for_gtarget(self, gtarget):
    if gtarget >= 100e-6:
        return self.wgc.WGFMU_MEASURE_CURRENT_RANGE_1MA
    elif gtarget >= 2e-6:
        return self.wgc.WGFMU_MEASURE_CURRENT_RANGE_100UA
    elif gtarget >= 0.1e-6:  
        return self.wgc.WGFMU_MEASURE_CURRENT_RANGE_1UA
    else:
        raise ValueError(f"Target conductance {gtarget} S is too small for reliable WGFMU measurement.")
    