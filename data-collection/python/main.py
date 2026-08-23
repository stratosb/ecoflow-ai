import datetime, time, os
from arduino.app_utils import App, Bridge
import csv

textname = "saturated"
filename = ""
previous_timestamp = 0
counter = 0

def record_sensor_samples(temperature: float, humidity: float, moisture: int):
    if temperature is None or humidity is None or moisture is None:
        print("Received invalid sensor samples: temperature=%s, humidity=%s, moisture=%s" % (temperature, humidity, moisture))
        return

    timestamp = int(datetime.datetime.now().timestamp() * 1000)

    print(filename)
    print(timestamp)
    print(previous_timestamp)
    
    if (timestamp - previous_timestamp) >= 5 * 60 * 1000:    # 5 minutes have passed
        increment_counter()
        update_timestamp(timestamp)
        update_filename(textname + "_" + str(counter) + ".csv")

    # Write samples to csv file
    write_to_file(filename , timestamp, round(temperature,2), round(humidity,2), moisture)


def write_to_file(filename: str, timestamp: datetime, temperature: float, humidity: float, moisture: int):
    file_exists = os.path.isfile(filename)
    
    # Create file and write header once
    with open(filename, "a", newline="") as f:
        writer = csv.writer(f)

        if not file_exists:
            # Header
            writer.writerow(["timestamp", "temperature", "humidity", "moisture"])

        writer.writerow([timestamp, temperature, humidity, moisture])
        f.flush()  # ensure data is written to disk
        
    print(temperature, humidity, moisture)


def increment_counter():
    global counter
    counter += 1

def update_timestamp(timestamp: datetime):
    global previous_timestamp
    previous_timestamp = timestamp

def update_filename(name: str):
    global filename
    filename = name


print("Registering 'record_sensor_samples' callback.")
Bridge.provide("record_sensor_samples", record_sensor_samples)

print("Starting App...")
App.run()