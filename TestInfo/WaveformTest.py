waveform_data = """Start\t0.0\t0.0\t0
Ramp Up\t1.0\t1.0\t1.8\t1ua
Hold\t2.0\t2.0\t1.8
Ramp Down\t3.0\t3.0\t0\t10ua
End\t4.0\t4.0\t0"""

with open("waveform_example.txt", "w") as file:
    file.write(waveform_data)
