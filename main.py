import requests
import matplotlib.pyplot as plt
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

BASIS_URL = "https://api.luchtmeetnet.nl/open_api"

def haal_fijnstofmetingen_op(station_nummer, startdatum, einddatum):
    eindpunt = f"{BASIS_URL}/measurements"
    params = {
        "station_number": station_nummer,
        "start_date": startdatum,
        "end_date": einddatum,
    }
    response = requests.get(eindpunt, params=params)
    if response.status_code == 200:
        data = response.json()
        pm10_metingen = [m for m in data['data'] if m['formula'] == 'PM10']
        pm25_metingen = [m for m in data['data'] if m['formula'] == 'PM2.5']
        return pm10_metingen, pm25_metingen
    else:
        print(f"Error: {response.status_code}")
        return None, None

def haal_stations_op():
    eindpunt = f"{BASIS_URL}/stations"
    response = requests.get(eindpunt)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None

def verzamel_metingen_voor_station(station, startdatum, einddatum):
    station_nummer = station['number']
    return haal_fijnstofmetingen_op(station_nummer, startdatum, einddatum)

def verzamel_alle_metingen(startdatum, einddatum):
    stations = haal_stations_op()
    alle_pm10_metingen = []
    alle_pm25_metingen = []
    
    if stations:
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(verzamel_metingen_voor_station, station, startdatum, einddatum) for station in stations['data']]
            for future in as_completed(futures):
                pm10_metingen, pm25_metingen = future.result()
                if pm10_metingen:
                    alle_pm10_metingen.extend(pm10_metingen)
                if pm25_metingen:
                    alle_pm25_metingen.extend(pm25_metingen)
                    
    return alle_pm10_metingen, alle_pm25_metingen

def maak_grafiek(metingen, stof_type, bestand_naam):
    tijden = [datetime.strptime(m['timestamp_measured'], '%Y-%m-%dT%H:%M:%S%z') for m in metingen]
    waarden = [m['value'] for m in metingen]
    
    plt.figure(figsize=(10, 6))
    plt.plot(tijden, waarden, label=stof_type)
    plt.xlabel('Tijd')
    plt.ylabel(f'{stof_type} Concentratie (µg/m³)')
    plt.title(f'{stof_type} Concentratie over Tijd')
    plt.legend()
    plt.grid(True)
    plt.savefig(bestand_naam)
    plt.close()

if __name__ == "__main__":
    startdatum = "2023-05-01"
    einddatum = "2023-05-07"
    
    alle_pm10_metingen, alle_pm25_metingen = verzamel_alle_metingen(startdatum, einddatum)
    
    if alle_pm10_metingen:
        maak_grafiek(alle_pm10_metingen, 'PM10', 'PM10_concentratie.png')
    if alle_pm25_metingen:
        maak_grafiek(alle_pm25_metingen, 'PM2.5', 'PM25_concentratie.png')
