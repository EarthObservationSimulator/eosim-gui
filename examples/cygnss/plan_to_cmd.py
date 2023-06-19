"""
The script needs to be verified. It converts the plan file into command json file in the format accepted by esoim-gui.
It only processed the observations, and not the downlinks.
"""
import csv
import json
import datetime

######## define the epoch and step size ########
# epoch must be in UTC
year = int(2020)
month = int(8)
day = int(1)
hour= int(0)
min = int(0)
sec = int(0)
# define step size
step_size = 1 # step size in second

######## define the paths to the grid and plan files ########
grid_fl = 'Grid_WLFP_Day_1_Aug_1_2020.csv'
plan_fl = 'planSim.CYG41886.txt'

######## define the path to the resulting command json file ########
cmd_fl = 'cmd_temp.json'

################################################################
epoch = datetime.datetime(year, month, day, hour, min, sec)
#epoch = epoch.isoformat() + 'Z'

# Read the coordinates file and store data in a dictionary
coordinates = {}
with open(grid_fl, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        coordinates[int(row['GP index'])] = [float(row['lon [deg]']), float(row['lat [deg]']), 0]

# Function to process a line from the plan file
def process_plan_line(line, line_idx):
    parts = line.split(', ')
    time_index = int(parts[0].split(': ')[1])
    type = parts[1]
    if type == 'RAW':
        # Find the targets part, remove trailing newlines, and get the numbers
        targets_part = parts[6:]    
        separator = ','
        targets_str = separator.join(targets_part)
        targets_str = targets_str.strip("targets: ")
        targets_str = targets_str.strip("[]\n")
        # Split the string into individual elements
        targets_list = targets_str.split(",")
        # Convert each element to an integer
        targets = [int(element) for element in targets_list]
        observed_positions = [coordinates[i] for i in targets]

        # find the start and stop time in ISO-8601 standard
        intervalSeconds = step_size * time_index
        startTime = (epoch + datetime.timedelta(0, intervalSeconds)).isoformat() + 'Z'
        intervalSeconds = intervalSeconds + 1
        stopTime = (epoch + datetime.timedelta(0, intervalSeconds)).isoformat() + 'Z'

        return {"@id": f"ANI-{line_idx:08d}",
                "@type": "TakeImage",
                "spacecraftId": "CYG41886",
                "startTime": startTime,
                "stopTime": stopTime,
                "observedPosition": {
                    "@type": "cartographicDegrees",
                    "cartographicDegrees": observed_positions
                },
                "color": {
                    "rgba": [255, 0, 0, 255]
                }}


# Read the plan file and process each line
results = []
with open(plan_fl, 'r') as plan_file:
    line_idx = 0
    for line in plan_file:
        if 'RAW' in line:  # Only process 'RAW' lines
            results.append(process_plan_line(line, line_idx))
        line_idx = line_idx + 1


# write the resutls
with open(cmd_fl, "w") as json_file:
    # Write the dictionary as JSON data to the file
    json.dump(results, json_file, indent=4)