import numpy as np
import matplotlib.pyplot as plt
import datetime
from IPython.display import display, clear_output

def prg_2terminal(self, b1500=None, param_name=None, v_prg = 1, v_rst = -1, v_prg_max = 9.8, v_rd = .1, vstep = 0.1, gmin = 300e-6, gmax = 1000e-6, pulses_per_voltage = 30, ranging_rd = 6002, read_waveform = "Evan_Reram_4", program_waveform = "Evan_Reram_4", **overrides):

    now = datetime.datetime.now()
    date_time = now.strftime("%Y-%m-%d_%H-%M-%S")

    final_params = {
        "v_prg": v_prg,
        "v_prg_max": v_prg_max,
        "v_rst": v_rst,
        "v_rd": v_rd,
        "vstep": vstep,
        "gmin": gmin,
        "gmax": gmax,
        "pulses_per_voltage": pulses_per_voltage,
        "ranging_rd": ranging_rd,
        "read_waveform" : read_waveform,
        "program_waveform" : program_waveform
    }

    if b1500 and param_name:
        param_block = dict(b1500.parameters.get(param_name, {}))
        param_block.update(overrides)
        for key, value in param_block.items():
            setattr(b1500, f"{key}_{param_name}", value)
        final_params.update(param_block)

    if not b1500 or not param_name:
        final_params.update(overrides)

    v_prg = final_params["v_prg"]
    v_rst = final_params["v_rst"]
    v_prg_max = final_params["v_prg_max"]
    v_rd = final_params["v_rd"]
    vstep = final_params["vstep"]
    gmin = final_params["gmin"]
    gmax =  final_params["gmax"]
    pulses_per_voltage = final_params["pulses_per_voltage"]
    ranging_rd  = final_params["ranging_rd"]
    read_waveform = final_params["read_waveform"]
    program_waveform = final_params["program_waveform"]
    
    times = 0
    currents = 0
    conductances = 0
    v_prg_set = v_prg
    v_prg_rst = v_rst

    pulse_num = 0
    pulse_count = []               # Sequential pulse index
    conductance_history = []       # Recorded conductances

    fig, ax = plt.subplots()
    ax.set_xlabel("Pulse Count")
    ax.set_ylabel("Conductance (S)")
    ax.set_title("Conductance vs Pulse Count")
    ax.grid(True)
    display(fig)

    done = False
    results = self.rd_pulses_Resalat(b1500, alternate_waveform = read_waveform, v_rd = v_rd, ranging_rd = ranging_rd)
    g_cur = sum(results[2]) / len(results[2])

    if (g_cur >= gmin) and (g_cur <= gmax):
        done = True

    vstep_increment = 0

    while done == False and abs(v_prg) <= abs(v_prg_max):
        set_done = (g_cur >= gmin)
        rst_done = (g_cur <= gmax)
        done = np.all(set_done & rst_done)

        if not set_done:
            v_prg_set += vstep_increment
            v_prg = v_prg_set
            operation = "SET"
        elif not rst_done:
            v_prg_rst -= vstep_increment
            v_prg = v_prg_rst
            operation = "RESET"

        print(f"value of conductance {g_cur:.4g}, SET {set_done}, RESET {rst_done}, and DONE {done} Trying to reach between: ({gmin}, {gmax})\nProgramming Voltage of: {v_prg}V\n")

        self.wg.WGFMU_clear()
        self.create_waveform(b1500, alternate_waveform = program_waveform, OverrideValue = [("program", v_prg), ("comp", ranging_rd)])
        self.wgfmu_run([b1500.test_info.ch_vdd , b1500.test_info.ch_vss], open_first=True, close_after=True)

        times1, vals1 = self.read_results(b1500.test_info.ch_vdd)
        times2, vals2 = self.read_results(b1500.test_info.ch_vss)

        times = times1
        currents = vals1
        conductances = currents / v_rd
        g_cur = conductances[-1]
        current = currents[-1]

        # === Append and Plot ===
        pulse_count.append(len(pulse_count))
        conductance_history.append(g_cur)

        ax.clear()
        ax.plot(pulse_count, conductance_history, marker='o', linestyle='-')
        ax.set_xlabel("Pulse Count")
        ax.set_ylabel("Conductance (S)")
        ax.set_title("Conductance vs Pulse Count")
        ax.grid(True)
        ax.set_ylim(min(conductance_history) * 0.95, max(conductance_history) * 1.05)

        clear_output(wait=True)
        display(fig)

        pulse_num += 1
        if pulse_num < pulses_per_voltage:
            vstep_increment = 0
        else:
            vstep_increment = vstep
            pulse_num = 0

        if abs(v_prg) > abs(v_prg_max):
            print(f"The device is unprogrammable - Bias Condition Is Over {v_prg_max} V")
        elif done:
            print(f"The program operation succeeds with conductance of {g_cur*1e6:.4g} uS \t at bias condition {v_prg:.4g} V \t  ({current*1e6:.3g} uA)")

    plt.close(fig)
    return (times, currents, g_cur, conductances)
