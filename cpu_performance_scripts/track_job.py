#!/usr/bin/env python
"""
track_job.py: "Track the progress of your simulation. Run this script as a background process."

Usage: track_job.py [options]

Options:
    -h, --help                  Show this screen
    --out_dir=<output>          Path to the output folder [default: ../output/]
"""


## ------------------------------------------------ ##
## ------------------------------------------------ ##
## Code was taken from Vasilii Pustovoit, modified
## and enhanced by Shivan Khullar
## ------------------------------------------------ ##
## ------------------------------------------------ ##


import os
import time
import csv
from docopt import docopt
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Define the event handler
class CPUHandler(FileSystemEventHandler):
    def __init__(self, output_csv):
        self.output_csv = output_csv

    def on_modified(self, event):
        if "cpu.txt" in event.src_path:
            with open(event.src_path, 'r') as f:
                lines = f.readlines()[-35:]
                data = {}
                for line in lines:
                    if "Step" in line:
                        data['Simulation Time'] = float(line.split(',')[1].split()[1])
                        data['Real World Time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        print (data)
                    else:
                        parts = line.strip().split()
                        if len(parts) > 1:
                            key = parts[0]
                            value = parts[1]
                            data[key] = value

                # Write to CSV
                with open(self.output_csv, 'a', newline='') as csv_file:
                    writer = csv.DictWriter(csv_file, fieldnames=data.keys())
                    writer.writerow(data)

def track_simulation_progress(base_dir):
    # Define the base output directory
    #base_dir = "./output"
    
    # Construct paths
    cpu_txt_path = os.path.join(base_dir, 'cpu.txt')
    output_csv_path = os.path.join(base_dir, 'progress.csv')

    # Initialize CSV file if it doesn't exist
    if not os.path.exists(output_csv_path):
        with open(output_csv_path, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            # Initial dummy write to determine the fieldnames from the first read
            with open(cpu_txt_path, 'r') as f:
                lines = f.readlines()[-35:]
                data = {}
                for line in lines:
                    parts = line.strip().split()
                    if len(parts) > 1:
                        key = parts[0]
                        value = parts[1]
                        data[key] = value
                dict_writer = csv.DictWriter(csv_file, fieldnames=data.keys())
                dict_writer.writeheader()

    event_handler = CPUHandler(output_csv=output_csv_path)
    observer = Observer()
    observer.schedule(event_handler, path=base_dir, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    args = docopt(__doc__)
    out_dir = args['--out_dir']
    if out_dir[-1] != "/":
        out_dir += "/"
    
    track_simulation_progress(out_dir)
