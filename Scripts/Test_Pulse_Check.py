from B1500.B1500Unified import B1500
import numpy as np
import matplotlib.pyplot as plt
import time

#What if we had a program that simply biased the Gate and then every 5 minutes it checks the Conductance of the drain and spits out what happens
#So I can make a program that automatically goes through each voltage and checks and waits until the conductance levels off so I can see change 
#in confuctance versus voltage and how long it takes to program each state for each voltage cause what if lower conductance/Higher voltage states
#are arived at faster compared to the change in conductance

# Define experiment parameters
parameters = {
    "Name": "Evan",
    "Test Number": "3090",
    "Die Number": 1,
    "Device Number": 53,
    "Waveform Format": "Reram",  # Loads "Reram.txt"
    "Waveform": "Evan_Reram_4",

    # "Waveform Editor": "ask",   
    "VDD WGFMU": 1,
    "VSS WGFMU": 2,
    "Interval": 1.5e-3,
    "data_points": 300,

    #Device Read Values
    "v_rd": 1,
    "Wait": 1, #in seconds
    "g_min_tolerance": 0.25e-11, #Change These
    "g_max_tolerance": 0.25e-11,  #Change These

    #Bias Values for Programming
    "Gate_Bias": -10,
    "Drain_Bias": 0,
    "Source_Bias": 0,
    "Base_Bias": 0,

    #Initial Sweep Values
    "Start": 0,
    "Stop": 1,
    "Steps": 101,
    "Mode": 3, #Double Sweep Change to 1 for single
    "ICompliance": .1,
    
    #Heres my probe setup
    "smu_numD": 4,
    "smu_numG": 1,
    "smu_numS": 2,
    "smu_numB": 3
}

# Initialize Unified B1500 (includes parameter validation)
b1500 = B1500(unit_label = 'A', parameters=parameters)


# b1500.smu.IVSweep(smu_numD, vstart=b1500.Start, vstop=b1500.Stop , nsteps=b1500.Steps, mode=b1500.Mode, icomp=b1500.ICompliance, connect_first=True, disconnect_after=True , plot_data=True)

#Next get Initial Conductance:
read_initial = b1500.smu.smu_meas_spot_4terminal(smu_numD=4, smu_numG=1, smu_numS=3, smu_numB=2, VDbias = b1500.v_rd, VGbias = 0,VSbias = 0, VBbias = 0 , vmeas=0.1 , icomp=100e-3 , reset_timer=True , disconnect_after=False, activate_smus = True )

#This steps takes the raw B1500 data and turns it into clean collumns we can use
data = b1500.data_clean(b1500, read_initial, parameters, NoSave = True)
time_drain = data.get("SMU4_Time", None)
current_drain = data.get("SMU4_Current", None)

#Now we take the data and put it into useful variables and set our initial conductance
current_initial = float(current_drain[0])
time_initial = float(time_drain[0])
cond_initial = current_initial
g_d = cond_initial
print(f"\nTHE INITIAL CONDUCTANCE IS: {g_d*1e9}nS")

#Instantiate empty dataframe for storing my in progress data
all_data = np.empty((0, 4))  # 0 rows, 2 columns for storing pairs of floats

#Throw out first 50 point since this might follow a different equation
First_50_Done = False

#Total time biased in seconds
Total_Time_Biasing = 0

# Initialize a flag to print the "start averaging" message only once
started_averaging = False

#Flags for looping through my checks for if the conductance has leveled out
initial_run  = True #flag so I can do fast looping
last_run = False
GLEVEL = False
g_d_new = 0

# Initialize lists to store the last 50 and the most recent 25 readings for rolling average of conductance measurements
last_50_readings = []
last_25_readings = []

#Empty dataframe for storing the first 50 data points since they seem to behave differently than the rest
first_50 = np.empty((0, 2)) #First 50 data readings since it kinda looks like it might follow a different equation

# Function to compute the average of a list of readings
def compute_average(readings):
    print(f"input array has length of: {len(readings)}")
    return sum(readings) / len(readings) if readings else 0



try:
    #Now lets loop between Setting a DC Bias on the gate and then stopping bias after a certain time, Reading the conductance on the Drain, then looping until the drain conductance levels off
    while not GLEVEL: #am I leveled off or saturated conductance

        if last_run: #am I done? if yes then disconnect all SMUS
            b1500.smu.disconnect_smu_list([1, 2, 3, 4]) #Hey Clean this up Later
            break

        #Bias Just the Gate and leave everything else at 0
        b1500.smu.bias_smu(b1500.smu_numD, b1500.Drain_Bias, Icomp=100e-3)
        b1500.smu.bias_smu(b1500.smu_numG, b1500.Gate_Bias, Icomp=.1)
        b1500.smu.bias_smu(b1500.smu_numS, b1500.Source_Bias, Icomp=100e-3)
        b1500.smu.bias_smu(b1500.smu_numB, b1500.Base_Bias, Icomp=100e-3)

        #Wait for a certain amount of time
        print(f"Waiting for {b1500.Wait} seconds")
        time.sleep(b1500.Wait)  # Pauses execution for a variable number of seconds
        print("Done waiting!")
        Total_Time_Biasing += b1500.Wait


        
        if initial_run: #check for fast looping
            activate_smus = False
            disconnect_after = False
        else:
            activate_smus = False

        if last_run: #Not really needed since we break on last run earlier
            disconnect_after = True

        #Get my conductance after biasing the Gate for so long
        read_initial = b1500.smu.smu_meas_spot_4terminal(smu_numD=4, smu_numG=1, smu_numS=3, smu_numB=2, VDbias = b1500.v_rd, VGbias = 0,VSbias = 0, VBbias = 0 , vmeas=0.1 , icomp=100e-3 , reset_timer=True , disconnect_after=disconnect_after, clear_settings = True, activate_smus = activate_smus)
        
        data = b1500.data_clean(b1500, read_initial, parameters, NoSave = True)
        time_drain = data.get("SMU4_Time", None)
        current_drain = data.get("SMU4_Current", None)

        current_initial = float(current_drain[0])
        time_initial = float(time_drain[0])
        cond_initial = current_initial/1 
        g_d_new = cond_initial
    
        
       
        
        #Check if conductance has leveled off
        # Ensure we have at least 50 readings before starting the comparison
        if len(last_50_readings) >= 100:
            # Compute the averages of the last 50 and most recent 25 readings
            avg_last_50 = compute_average(last_50_readings)
            avg_last_25 = compute_average(last_25_readings)
            difference = avg_last_25 - avg_last_50
            
            # Print the "start averaging" message only once
            if not started_averaging:
                print("\n*\n*\nStarted averaging after receiving 100 readings.\n*\n*\n")
                started_averaging = True
                
                
            # Print averages and the difference
            print(f"\n*\n*\nAverages:\nLast 100 Average: {avg_last_50}\nLast 50 Average: {avg_last_25}\nDifference: {difference}\n")
            print(f"This Device has been Biased at {b1500.Gate_Bias}, for {Total_Time_Biasing} seconds!\n*\n*\n")
            # Example float values to append
            new_data = [time_initial, g_d_new, avg_last_50, difference]

            # Append the new data (a pair of floats) to the all_data array
            all_data = np.append(all_data, [new_data], axis=0)
            
            # Check if the rolling averages are within the target range and not equal to the previous value
            if ((avg_last_25 > (avg_last_50 - b1500.g_min_tolerance)) and 
                (avg_last_25 < (avg_last_50 + b1500.g_max_tolerance)) and 
                (avg_last_25 != avg_last_50)):
                
                GLEVEL = True
                last_run = True

        #This statement is to save our first 50 entries and then start the averaging after the first 50       
        elif (not First_50_Done) and (len(last_50_readings) >= 50):
            b1500.save_numpy_to_csv(b1500.test_info, first_50, filename = "Evan_First_50_Readings")
            First_50_Done = True
        
        #This statement is used to add to the averaging "Window" that shift to add in the newest value and then later pop the 51st value off so the window only encompasses the last
        # 50 Datapoints 
        else:
            # If less than 50 readings, just append the new reading and continue
            if not First_50_Done:
                first_50_add = [time_initial, g_d_new]
                first_50 = np.append(first_50, [first_50_add], axis=0)
                
            else:
                last_50_readings.append(g_d_new)
                last_25_readings.append(g_d_new)
            
        
        # Insert the new reading into both lists for rolling average
        # Always append the new reading to both lists
        last_50_readings.append(g_d_new)
        last_25_readings.append(g_d_new)
        
        # Remove the oldest reading from both lists to maintain the size
        if len(last_50_readings) > 100:
            last_50_readings.pop(0)
        if len(last_25_readings) > 50:
            last_25_readings.pop(0)

                
except KeyboardInterrupt:
    print("Keyboard Interrupt detected. Saving the data...")
    
    #Ground all SMUs To stop any previous commands from sneaking through
    b1500.smu.bias_smu(b1500.smu_numD, 0, Icomp=100e-3)
    b1500.smu.bias_smu(b1500.smu_numG, 0, Icomp=.1)
    b1500.smu.bias_smu(b1500.smu_numS, 0, Icomp=100e-3)
    b1500.smu.bias_smu(b1500.smu_numB, 0, Icomp=100e-3)
    
    for i in range(1):   
        read_initial = b1500.smu.smu_meas_spot_4terminal(smu_numD=4, smu_numG=1, smu_numS=3, smu_numB=2, VDbias = b1500.v_rd/10, VGbias = 0,VSbias = 0, VBbias = 0 , vmeas=0.1 , icomp=100e-3 , reset_timer=True , disconnect_after=False, clear_settings = True, activate_smus = False)
        
        data = b1500.data_clean(b1500, read_initial, parameters, NoSave = True)
        time_drain = data.get("SMU4_Time", None)
        current_drain = data.get("SMU4_Current", None)
    
        current_initial = float(current_drain[0])
        time_initial = float(time_drain[0])
        cond_initial = current_initial / (b1500.v_rd/10)
        g_d_new = cond_initial
        
        # Example float values to append
        new_data = [time_initial, g_d_new, avg_last_50, difference]
    
        # Append the new data (a pair of floats) to the all_data array
        all_data = np.append(all_data, [new_data], axis=0)
        
        print(f"Waiting for {b1500.Wait} seconds")
        time.sleep(b1500.Wait)  # Pauses execution for a variable number of seconds
        print("Done waiting!")
        
        print(f"\n*\n*\nPrevious: {g_d}, New: {g_d_new}, Difference: {g_d_new - g_d}\n*\n*\n")
    
    #Disconnect
    b1500.connection.write("CL")
    
    # Save the data to CSV using your save function
    b1500.save_numpy_to_csv(b1500.test_info, all_data, filename="Evan_Conductance")
    print("Data saved successfully.")

print(f"My Voltage: {b1500.Gate_Bias}V Gives me a Conductance of: {avg_last_25}S Which is down from my initial Conductance: {g_d}")
b1500.connection.write("CL")
b1500.save_numpy_to_csv(b1500.test_info, all_data, filename = "Evan_Conductance")