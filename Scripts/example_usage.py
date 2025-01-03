from B1500_SMU.B1500_SMU_Core import B1500_SMU

# Initialize the B1500Core object
b1500 = B1500_SMU()

# Use core and dynamically loaded methods
print(b1500.core_method())  # Output: This is a core method of B1500Core.
b1500.TestAddress()
print(b1500.perform_iv_sweep(0, 5, 0.1))  # Output: Performing IV sweep from 0 to 5 with step 0.1.