import requests
import datetime
from datetime import datetime
import time


def log(message):
    log_line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n"
    with open("bus_log.txt", "a", encoding="utf-8") as f:
        f.write(log_line)

log("Script starting ...")


last_seen_at_stop = {
    'Zoo': set(),
    'Toompark': set()
}

def log_arrival(stop_name, timestamp, vehicle_id):
    filename = f'C:/Users/subbi/Documents/RMK-data-team-internship---test-challenge-2025/bus_arrival_{stop_name.lower()}.txt'
    with open(filename, 'a', encoding='utf-8') as file:
        file.write(f"|{timestamp}| - Bus 8 (ID {vehicle_id}) arrived at bus stop: /{stop_name}/\n")

def fetch_bus_locations():
    url = 'https://transport.tallinn.ee/gps.txt'
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            log("Error occured whild downloading data.")
            return
    except Exception as e:
        log(f"Network issue: {e}")
        return

    now = datetime.datetime.now().strftime('%H:%M:%S')
    lines = response.text.strip().split('\n')

    current_seen = {
        'Zoo': set(),
        'Toompark': set()
    }

    for line in lines:
        parts = line.strip().split(',')
        if len(parts) < 11:
            continue

        vehicle_id = parts[0]
        line_number = parts[6]
        stop_name = parts[10]

        if line_number == '8' and stop_name in ['Zoo', 'Toompark']:
            current_seen[stop_name].add(vehicle_id)
            if vehicle_id not in last_seen_at_stop[stop_name]:
                log_arrival(stop_name, now, vehicle_id)

    for stop in ['Zoo', 'Toompark']:
        last_seen_at_stop[stop] = current_seen[stop]
        log(f"Bus 8 arrived at {stop} – {datetime.now().strftime('%H:%M:%S')}")
def main():
    log("Starting cycle (8:00–9:06)...")
    while True:
        now = datetime.datetime.now()
        if now.hour == 8 or (now.hour == 9 and now.minute < 6):
            log('fetching data')
            fetch_bus_locations()
            time.sleep(60)
        else:
            log("end time – current time is outside 8:00–9:05.")
            break

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(f"Error occured during script execution: {e}")
