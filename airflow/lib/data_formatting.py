import pandas as pd
import os
import json


def format_station_details_data(input_path):
    """
    Converts a JSON file at a given path to a Parquet file in a corresponding 'formatted' directory.
    """
    # Split the input path to change 'raw' to 'formatted' in the path
    parts = os.path.normpath(input_path).split(os.sep)
    if 'raw' in parts:
        parts[parts.index('raw')] = 'formatted'
    
    formatted_dir = os.sep.join(parts[:-1])  # Directory part of the path
    formatted_file = parts[-1].replace('.json', '.snappy.parquet')
    formatted_path = os.path.join(formatted_dir, formatted_file)

    # Ensure the directory exists
    if not os.path.exists(formatted_dir):
        os.makedirs(formatted_dir)

    try:
        with open(input_path, 'r') as file:
            data = json.load(file)
        
        # Initialize a list to store station data
        stations_data = []
        
        # Iterate over each station in the JSON data
        for station in data['data']['stations']:
            station_info = {
                "station_id": station["station_id"],
                "name": station["name"],
                "latitude": station["lat"],
                "longitude": station["lon"],
                "capacity": station["capacity"],
                "station_opening_hours": station.get("station_opening_hours")  # Use .get for optional fields
            }
            stations_data.append(station_info)
        
        # Create a DataFrame from the list of station data
        final_df = pd.DataFrame(stations_data)
        
        # Save DataFrame as a Parquet file
        final_df.to_parquet(formatted_path, compression='snappy')
    except Exception as e:
        print(f"Error processing file {input_path}: {e}")



def format_velib_data(input_path):
    """
    Converts a JSON file at a given path to a Parquet file in a corresponding 'formatted' directory.
    """
    parts = os.path.normpath(input_path).split(os.sep)
    if 'raw' in parts:
        parts[parts.index('raw')] = 'formatted'
    
    formatted_dir = os.sep.join(parts[:-1]) 
    formatted_file = parts[-1].replace('.json', '.snappy.parquet')
    formatted_path = os.path.join(formatted_dir, formatted_file)

    # Ensure the directory exists
    if not os.path.exists(formatted_dir):
        os.makedirs(formatted_dir)

    with open(input_path, 'r') as file:
        data = json.load(file)
    
    stations_data = []
    try:
        for station in data['data']['stations']:
            station_info = {
                "station_id": station["station_id"],
                "num_bikes_available": station["num_bikes_available"],
                "num_docks_available": station["num_docks_available"],
                "is_installed": station["is_installed"],
                "is_returning": station["is_returning"],
                "is_renting": station["is_renting"],
                "last_reported": station["last_reported"],
            }
            
            if "num_bikes_available_types" in station:
                for bike_type in station["num_bikes_available_types"]:
                    if "mechanical" in bike_type:
                        station_info["mechanical_bikes_available"] = bike_type["mechanical"]
                    if "ebike" in bike_type:
                        station_info["ebikes_available"] = bike_type["ebike"]
            
            stations_data.append(station_info)
        
        final_df = pd.DataFrame(stations_data)
            
            # Save DataFrame as a Parquet file
        final_df.to_parquet(formatted_path, compression='snappy')
    except Exception as e:
        print(f"Error processing file {input_path}: {e}")


