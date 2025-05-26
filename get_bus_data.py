import polars as pl
import pandas as pd
import os
import zipfile
import requests
from datetime import datetime, timedelta
from conf import URL,ZIPFILE,DATA_FOLDER_PATH,STOPS_PATH,STOP_TIMES_PATH,TRIPS_PATH,ROUTES_PATH,CALENDAR_PATH

def download_data_zip(url:str = None)-> bool:
    """ Function for downloading public transportation data folder from pilet.ee,
    function creates a bus_data.zip file.
    
    Args:
        url (str, optional): url for download data. Defaults to None.
    Returns:
        bool:returns True if download was successful otherwise False.     
    """    
    try:
        response = requests.get(URL) if url == None else requests.get(url)
        
        if response.status_code == 200:
            with open(ZIPFILE, "wb") as f:
                f.write(response.content)
            print("ZIP-file downloaded succesfully:", ZIPFILE)
            return True
        else:
            print("Download failed, status:", response.status_code)
            return False
    except EOFError:
         print("Download was unsuccesful, Unexpected Error.")
         return False
         
def get_bus_data(update_data:bool = False)->int:
    """ The function checks if the folder bus_data or the file bus_data.zip exists.
    If neither exists, it downloads bus_data.zip, extracts its contents, and then deletes the bus_data.zip file.
    If the file bus_data.zip already exists then it extracts its contents, and then deletes the bus_data.zip file.
    
    Args:
        update_data (bool, optional): Value for deciding whether or not update existing data. Defaults to False.
    
    Returns:
        int: returns 0 if the bus_data folder already exists otherwise 1.
    """  
    
    if os.path.exists(DATA_FOLDER_PATH):
        print('Data already exists.')
        if update_data:
            if download_data_zip():
                os.remove(DATA_FOLDER_PATH)
            else:
                print('Data could not be updated at this time check your internet conncetion and try again.')
                return 0
        else:
            return 0
    
    elif not os.path.exists(ZIPFILE):
        print('File does not exist, trying to download .zip file')
        download_data_zip()
    else:
        print('Zip-file found')
    print(f'Extracting {ZIPFILE} ...')    
    with zipfile.ZipFile(ZIPFILE, 'r') as zip_ref:
        zip_ref.extractall(DATA_FOLDER_PATH)
    
    print('Zip-file extraction successful.')
    print(f'Deleting {ZIPFILE} ...')
    os.remove(ZIPFILE)
    print('Zip-file deletion was successful.')
    return 1

def filter_bus_data_pl(bus_nr: str = '8', route_name: str = 'Väike-Õismäe - Äigrumäe', start_stop: str = 'Zoo', end_stop: str = 'Toompark',start_time:str = '05:00:00',end_time:str = '09:30:00',weekdays:bool=False) -> list:
    """
    Function returns list containing choosen bus's departure time from the start_stop and arrival time at end_stop bus stop.

    Args:
        bus_nr (str, optional): Bus number. Defaults to '8'.
        route_name (str, optional): Name of the route that the bus drives. Defaults to 'Väike-Õismäe - Äigrumäe'.
        start_stop (str, optional):  Name of the starting bus stop. Defaults to 'Zoo'.
        end_stop (str, optional): Name of the end bus stop. Defaults to 'Toompark'.
        start_time (str, optional): Start of the time frame. Defaults to '05:00:00'.
        end_time (str, optional): End of the time frame. Defaults to '09:30:00'.
        weekdays (bool, optional): Parameter that determines whether to return weekend or weekday bus times. Defaults to True.

    Returns:
        list[]: [ [start_stop_departure_time(datetime.time()) , end_stop_arrival_time(datetime.time())], ... ]
    """
    # Loading in data files from bus_data
    stops = pl.read_csv(STOPS_PATH)
    stop_times = pl.read_csv(STOP_TIMES_PATH)
    trips = pl.read_csv(TRIPS_PATH)
    routes = pl.read_csv(ROUTES_PATH)
    calendar = pl.read_csv(CALENDAR_PATH)
    
    # selecting only busses that run on either weekdays or weekends
    calendar_match =  calendar.filter((pl.col('monday') == 1)) if weekdays else calendar.filter((pl.col('sunday') == 1))  
    
    # finding route_id for bus route 
    route_match = routes.filter(
        (pl.col('route_short_name') == bus_nr) & 
        (pl.col('route_long_name') == route_name)
    )
    
    # finding all the busses that have the choosen route and run on weekdays
    trips_match = trips.filter(
        (pl.col('route_id').is_in(route_match.select('route_id').to_series())) &
        (pl.col('trip_long_name') == route_name) &
        (pl.col('service_id').is_in(calendar_match.select('service_id').to_series()))
    )
    
    # finding all the bus stop departure times for all the trips_match busses and then joining them with stop info  
    stop_times_match = stop_times.filter(pl.col('trip_id').is_in(trips_match.select('trip_id').to_series().to_list()))
    stop_times_joined = stop_times_match.join(stops.select(['stop_id', 'stop_name']), on='stop_id', how='left')
    
    # finding the departure times from the starting bus stop
    departures = stop_times_joined.filter(pl.col('stop_name') == start_stop).select(['trip_id', 'departure_time'])
    departures = departures.with_columns(
        pl.col('departure_time').str.strptime(pl.Time, format='%H:%M:%S')
    )
    
    start_time_obj = datetime.strptime(start_time, "%H:%M:%S").time()
    end_time_obj = datetime.strptime(end_time, "%H:%M:%S").time()
    departures = departures.filter(
        (pl.col('departure_time') >= pl.lit(start_time_obj)) &
        (pl.col('departure_time') <= pl.lit(end_time_obj))
    )

    # finding the arrival times at the end bus stop 
    arrivals = stop_times_joined.filter(pl.col('stop_name') == end_stop).select(['trip_id', 'arrival_time'])
    arrivals = arrivals.with_columns(
        pl.col('arrival_time').str.strptime(pl.Time, format='%H:%M:%S')
    )
    arrivals = arrivals.filter(
        (pl.col('arrival_time') >= pl.lit(start_time_obj)) &
        (pl.col('arrival_time') <= pl.lit(end_time_obj))
    )

    # Joining departure times and arrival times based on trip_id
    combined = departures.join(arrivals, on='trip_id')
    combined_sorted = combined.sort('departure_time')

    # converting combined table to list
    result = combined_sorted.select(['departure_time', 'arrival_time']).to_numpy().tolist()

    return result

def calculate_probability_of_being_late(bus_times:list, walk_to_bus:int = 300, walk_to_work:int = 240, meeting_time:str = '09:05:00')-> list:
    """ Function calculates probability of being late depending on the departure time of the person, 
    and returns a list containing departure times and related probabilities.   

    Args:
        bus_times (list): [ [bus_leave_time(datetime.time()) , bus_arrive_time(datetime.time())], ... ]_
        walk_to_bus (int, optional): Time it takes to walk from home to the bus stop in seconds. Defaults to 300.
        walk_to_work (int, optional): Time it takes to walk from bus stop to the meeting in seconds. Defaults to 240.
        meeting_time (str, optional): Meeting start time "hours:minutes:seconds". Defaults to '09:05:00'.

    Returns:
        list:  [ [leave_time(str) , probability(int)], ... ]
    """
    #converting time values
    walk_to_bus = timedelta(seconds=walk_to_bus)
    walk_to_work = timedelta(seconds=walk_to_work)
    meeting_time = datetime.strptime(meeting_time,"%H:%M:%S")
   
    x_axis = []
    y_axis = []
    
    #insert_index and last_chance is used to add a data point exactly one second after the last viable bus has departed from the bus stop.
    insert_index = None
    last_chance = None
    
    for bus in bus_times:
        
        # Convert time objects to datetime for arithmetic
        arrive_at_work_dt = datetime.combine(meeting_time.date(), bus[1]) + walk_to_work
        home_departure_dt = datetime.combine(meeting_time.date(), bus[0]) - walk_to_bus
        
        #convert datetime object to string for x-axis labels
        home_departure_str = home_departure_dt.strftime("%H:%M")
        
        #probability logic 
        if arrive_at_work_dt <= meeting_time:
            x_axis.append(home_departure_str)
            y_axis.append(0)
            last_chance = home_departure_dt
            
        elif y_axis[-1] == 0:
            last_chance += timedelta(seconds=1)
            insert_index = len(y_axis)
            x_axis.append(home_departure_str)
            y_axis.append(1)
            
        else:
            x_axis.append(home_departure_str)
            y_axis.append(1)

    x_axis.insert(insert_index,last_chance.strftime("%H:%M"))
    y_axis.insert(insert_index,1)
            
    return [x_axis,y_axis]
