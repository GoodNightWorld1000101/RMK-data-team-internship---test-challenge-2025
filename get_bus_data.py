import pandas as pd
import os
import zipfile
import requests
from conf import URL,ZIPFILE,DATA_FOLDER_PATH,STOPS_PATH,STOP_TIMES_PATH,TRIPS_PATH,ROUTES_PATH

def download_data_zip()-> bool:
    """ Function for downloading public transportation data folder from pilet.ee,
    function creates a bus_data.zip file
    Returns:
        bool:returns 1 if download was successful otherwise 0.     
    """    
    try:
        response = requests.get(URL)
        
        if response.status_code == 200:
            with open(ZIPFILE, "wb") as f:
                f.write(response.content)
            print("ZIP-file downloaded succesfully:", ZIPFILE)
            return 1
        else:
            print("Download failed, status:", response.status_code)
            return 0
    except EOFError:
         print("Download was unsuccesful, Unexpected Error.")
         return 0
         
def get_bus_data(update_data:bool = False)->int:
    """ The function checks if the folder bus_data or the file bus_data.zip exists.
    If neither exists, it downloads bus_data.zip, extracts its contents, and then deletes the bus_data.zip file.
    If the file bus_data.zip already exists then it extracts its contents, and then deletes the bus_data.zip file.
    
    Args:
        update_data (bool): Value for deciding wheter or not update existing data by default False
    
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

def filter_bus_data(bus_nr: str = '8', route_name: str = 'Väike-Õismäe - Äigrumäe', start_stop: str = 'Zoo', end_stop: str = 'Toompark',start_time:str = '05:00:00',end_time:str = '09:10:00') -> list:
    """
    Function returns list containing choosen bus's departure time from the start_stop and arrival time at end_stop bus stop.

    Args:
        bus_nr (str): bus number by default '8'
        route_name (str): name of the route that the bus drives by default'Väike-Õismäe - Äigrumäe'
        start_stop (str):  name of the starting bus stop by default 'Zoo'
        end_stop (str): name of the end bus stop by default 'Toompark'
        start_time (str): start of the time frame by default '05:00:00'
        end_time (str): end of the time frame by default '09:10:00'

    Returns:
        list: [ [start_stop_departure_time , end_stop_arrival_time], ... ]
    """
    # Loading in data files from bus_data
    stops = pd.read_csv(STOPS_PATH)
    stop_times = pd.read_csv(STOP_TIMES_PATH)
    trips = pd.read_csv(TRIPS_PATH)
    routes = pd.read_csv(ROUTES_PATH)

    # finding choosen bus route and it's trip_id's
    route_match = routes[(routes['route_short_name'] == bus_nr) & (routes['route_long_name'] == route_name)]
    trips_match = trips[(trips['route_id'].isin(route_match['route_id'])) & (trips['trip_long_name'] == route_name)]
    stop_times_match = stop_times[stop_times['trip_id'].isin(trips_match['trip_id'])]
    stop_times_joined = stop_times_match.merge(stops[['stop_id', 'stop_name']], on='stop_id', how='left')

    # finding the departure times from the starting bus stop
    departures = stop_times_joined[stop_times_joined['stop_name'] == start_stop][['trip_id', 'departure_time']]
    departures['departure_time'] = pd.to_datetime(departures['departure_time'], format='%H:%M:%S').dt.time
    departures = departures[
        (departures['departure_time'] >= pd.to_datetime(start_time, format="%H:%M:%S").time()) &
        (departures['departure_time'] <= pd.to_datetime(end_time, format="%H:%M:%S").time())
    ]

    # finding the arrival times at the end bus stop 
    arrivals = stop_times_joined[stop_times_joined['stop_name'] == end_stop][['trip_id', 'arrival_time']]
    arrivals['arrival_time'] = pd.to_datetime(arrivals['arrival_time'], format='%H:%M:%S').dt.time
    arrivals = arrivals[
        (arrivals['arrival_time'] >= pd.to_datetime(start_time, format="%H:%M:%S").time()) &
        (arrivals['arrival_time'] <= pd.to_datetime(end_time, format="%H:%M:%S").time())
    ]

    # Joining departure times and arrival times based on trip_id
    combined = departures.merge(arrivals, on='trip_id')
    combined_sorted = combined.sort_values('departure_time')

    # converting combined table to list
    result = combined_sorted[['departure_time', 'arrival_time']].values.tolist()

    return result


