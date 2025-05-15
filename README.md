# RMK data team internship - test challenge 2025
The challenge is designed to demonstrate your style, statistical thinking, documentation and coding skills.
## The challenge
Rita works in RMK Tallinn office. She takes the Tallinn city bus number 8 from Zoo to Toompark (names of
bus stops) to get to work.
Rita has a meeting at 9:05 sharp every day from Monday to Friday. It takes her 300 seconds to walk from
home to the departure bus stop and 240 seconds to walk from the destination bus stop to the meeting
room.
Plot the probability of Rita being late to the meeting depending on the time she leaves home. (Assuming
she can only use the bus to get to work.)
It might look something like this:
![image](https://github.com/user-attachments/assets/f635bdd3-b692-4525-87a6-2db267df1b80)

## My solution
### First Day
First, I created a function to download public transportation data from `pilet.ee` and extract its contents into a folder named `bus_data`. 
Then, I wrote a function to filter the data based on the bus route, bus number, trip's starting bus stop, trip's ending bus stop, and a specified time frame. 
This function returns the departure and arrival times of the selected bus within the given time frame.

### TODO:
1.Create a function to calculate the probability of being late based on departure and arrival times.

2.Create a plot with probabilities on the Y-axis and departure times (i.e., leaving home) on the X-axis.

3.Consider whether holidays should be taken into account.

4.Test using polar against pandas

### Optional Tasks:
1.Create an input window for selecting the bus route, bus stops, and time frame.

2.Develop a reminder system that alerts the user about how many buses they have left before they're likely to be late.

3.Implement a "Forget the bus" feature that notifies the user they will be late if they wait for the next bus, and recommends alternatives like Bolt or a scooter instead.
