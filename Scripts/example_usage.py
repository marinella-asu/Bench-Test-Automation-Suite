from B1500_SMU.B1500_SMU_Core import B1500_SMU

# Initialize the B1500Core object
b1500 = B1500_SMU(gpib_address = 17, smu_channel_list = [301, 401, 501, 601])

# Use core and dynamically loaded methods
# print(b1500.core_method())  # Output: This is a core method of B1500Core.
# b1500.TestAddress()
# b1500.IVSweep(smu_num = 1, vstop = .01, icomp=100e-3, nsteps=100)
# b1500.smu_meas_spot_4termininal(smu_numD = 4, smu_numG = 1, smu_numS = 2, smu_numB = 3,VDbias = 0.01, VGbias = 0,VSbias = 0, VBbias = 0 , vmeas=0.01 , icomp=10e-3)
b1500.smu_meas_sample_multi_term(smu_numD = 1, smu_numG = 2, smu_numS = 3, smu_numB = 4, vmeasD = .01, vmeasG = 0, vmeasS = 0, vmeasB = 0, icompDSB = 10e-3, icompG = 10e-3,  interval = 1, pre_bias_time = 1, number = 1, disconnect_after=True, plot_results=False )
b1500.smu_meas_sample_multi_term(smu_numD = 1, smu_numG = 2, smu_numS = 3, smu_numB = 4, vmeasD = .01, vmeasG = 0, vmeasS = 0, vmeasB = 0, icompDSB = 10e-3, icompG = 10e-3,  interval = 1, pre_bias_time = 1, number = 1, disconnect_after=True, plot_results=False )