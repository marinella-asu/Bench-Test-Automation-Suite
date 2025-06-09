import pyvisa

gpib_str = f"GPIB0::17::INSTR"
rm = pyvisa.ResourceManager("C:\\Windows\\System32\\visa32.dll")
print(rm.list_resources())

connection = rm.open_resource(gpib_str)
print(connection.query("*IDN?"))

# import pyvisa

# rm = pyvisa.ResourceManager()  # use National Instruments backend
# # print("Resources found:", rm.list_resources())  # Should now show GPIB0::17::INSTR

# gpib_str = "GPIB0::17::INSTR"
# connection = rm.open_resource(gpib_str)
# print(connection.query("*IDN?"))

# import pyvisa
# from pyvisa import util

# print(util.get_library_paths())
