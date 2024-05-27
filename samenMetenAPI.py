import requests
import matplotlib.pyplot as plt
import pandas as pd

# Define the base URL for the API
base_url = "https://api-samenmeten.rivm.nl/v1.0"  # Update this to the correct base URL

# Function to get data from the API
def get_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")
    except ValueError as json_err:
        print(f"JSON decode error: {json_err}")
    return None

# Get all stations in Gelderland
def get_stations_in_gelderland():
    url = f"{base_url}/Things"
    data = get_data(url)
    gelderland_stations = []
    
    if data:
        print("Retrieved data from API:")
        print(data)  # Print the entire response for debugging
        
        for thing in data["value"]:
            description = thing.get("description", "")
            print(f"Station description: {description}")
            if "Gelderland" in description:
                gelderland_stations.append(thing)
    
    return gelderland_stations

# Get observations for a specific station and observed property (PM10 or PM2.5)
def get_observations(station_id, observed_property):
    url = f"{base_url}/Things({station_id})/Observations?$filter=ObservedProperty/name eq '{observed_property}'"
    data = get_data(url)
    observations = []

    if data:
        for observation in data["value"]:
            observations.append({
                "timestamp": observation["phenomenonTime"],
                "value": observation["result"]
            })
    
    return observations

# Plot data and save the figure
def plot_data(station_name, observed_property, observations):
    df = pd.DataFrame(observations)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df.set_index("timestamp", inplace=True)
    
    plt.figure(figsize=(10, 6))
    plt.plot(df.index, df["value"], label=observed_property)
    plt.xlabel("Time")
    plt.ylabel(f"{observed_property} Concentration (µg/m³)")
    plt.title(f"{observed_property} Levels at {station_name}")
    plt.legend()
    plt.grid(True)
    plt.savefig(f"{station_name}_{observed_property}.png")
    plt.close()

# Main function to execute the workflow
def main():
    stations = get_stations_in_gelderland()
    
    if not stations:
        print("No stations found in Gelderland.")
        return
    
    for station in stations:
        station_id = station["@iot.id"]
        station_name = station["name"]
        
        for observed_property in ["PM10", "PM2.5"]:
            observations = get_observations(station_id, observed_property)
            if observations:
                plot_data(station_name, observed_property, observations)

if __name__ == "__main__":
    main()
