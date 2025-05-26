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
picture of my final solution:
![image](https://github.com/user-attachments/assets/77174593-580f-443b-8c0a-3ca645efbb67)

### Dependencies

1. Used libraries:
- matplotlib.pyplot
- polars
- zipfile
- os
- requests
- datetime

Python version: Python 3.11.2
2. How downloaded data files are connected:
- `routes.txt` and `trips.txt` connect on `route_id` -> `trips.txt` and `calendar.txt` connect on `service_id` -> `trips.txt` and `stop_times.txt` connect on `trip_id` -> `stop_times.txt` and `stops.txt` connect on `stop_id`.


### First Day
First, I created a function to download public transportation data from `pilet.ee` and extract its contents into a folder named `bus_data`. 
Then, I wrote a function to filter the data based on the bus route, bus number, trip's starting bus stop, trip's ending bus stop, and a specified time frame. 
This function returns the departure and arrival times of the selected bus within the given time frame.

### Day 2/3 
I explored the idea of incorporating the probability of the bus being late and Rita twisting her ankle, but ultimately decided it might not be the right solution for this particular challenge.
I proceeded with the assumption that all given and derived values are constants, and the probability function should follow a Bernoulli distribution. Accordingly, I created a function, `calculate_probability_of_being_late`, which identifies the first instance of a bus being late. It assigns a value of 0 to all departure times that are less than or equal to the last viable departing bus minus the walking-to-bus-stop duration and a value of 1 to all that follow. Additionally, I included an extra data point—dated one second after the last viable bus departed—to more clearly indicate when the probability reaches 100%. After gathering my data points, I simply needed to plot them. I experimented with the plot design for a while until I found a suitable layout. Once the plot was ready, I made some small refinements to the previously created functions, mostly updating docstrings and adjusting comments. That’s when I realized I had made a mistake in the `filter_bus_data` function—I had forgotten to filter out buses that only run on weekends. As a result, my probability plot includes phantom buses that shouldn't be there.

picture of the current plot design(it has incorrect data):
![image](https://github.com/user-attachments/assets/d7f8b160-a691-4d97-9559-6d1b7c7d3f62)

### Day 4
I tested the `filter_bus_data` function using both Pandas and Polars and found that Polars was 7.5 times faster. As a result, I updated the `main.py` to use Polars based function instead of Pandas.
I also added weekdays parameter to `filter_bus_data` function so that you can choose whether to get weekday bus times or weekend bus times. 

### Optional Tasks(later plans for the project after the challenge results have been announced):
1.Create an input window for selecting the bus route, bus stops, and time frame.

2.Develop a reminder system that alerts the user about how many buses they have left before they're likely to be late.

3.Implement a "Forget the bus" feature that notifies the user they will be late if they wait for the next bus, and recommends alternatives like Bolt or a scooter instead.
