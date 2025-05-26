#TASK
'''
Rita works in RMK Tallinn office. She takes the Tallinn city bus number 8 from Zoo to Toompark (names of bus stops) to get to work.
Rita has a meeting at 9,05 sharp every day from Monday to Friday. 
It takes her 300 seconds to walk from home to the departure bus stop 
and 240 seconds to walk from the destination bus stop to the meeting room. 
Plot the probability of Rita being late to the meeting depending on the time she leaves home. 
(Assuming she can only use the bus to get to work.)
'''

from get_bus_data import filter_bus_data_pl, get_bus_data, calculate_probability_of_being_late
import matplotlib.pyplot as plt
#bus 8 timetable (Zoo peatusest) source:https://transport.tallinn.ee/#bus/8/a-b/00702-1

#downloading public transportation data if needed
data = get_bus_data()

#getting bus departure and arrival times
bus_dep_and_arr = filter_bus_data_pl() 

#getting values for x and y axis
leave_times, P_of_being_late = calculate_probability_of_being_late(bus_times=bus_dep_and_arr)

# Plot the result
plt.figure(figsize=(12, 6), facecolor='black')  # Set figure background color to black
plt.gca().set_facecolor('black')  # Set graph background color to black
plt.plot(leave_times, P_of_being_late, marker='o', color='orange')  # Set line color to orange and marker to circle

plt.xticks(rotation=45, color='gray',fontsize = 8)  # Set x-axis tick labels color to gray and rotate tick labels 45 degrees
plt.yticks(color='gray')  # Set y-axis tick labels color to gray

plt.xlabel("Rita leaving home [hour:min]", color='gray')
plt.ylabel("P(Rita being late to work) [%]", color='gray')
plt.title("Probability of Rita being late to the meeting depending on the time she leaves home", color='gray')

plt.grid(True, color='gray',axis='y')
plt.tight_layout()
plt.show()

