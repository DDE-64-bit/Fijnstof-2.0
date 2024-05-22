import os
import requests
import matplotlib.pyplot as plt
from datetime import datetime, timezone
import logging

logging.basicConfig(level=logging.INFO)

basisUrl = "https://api.luchtmeetnet.nl/open_api"
mapLocatie = "Grafieken"

os.makedirs(mapLocatie, exist_ok=True)

def haal_fijnstofmetingen_op(station_nummer, startdatum, einddatum):
    eindpunt = f"{basisUrl}/measurements"
    params = {
        "station_number": station_nummer,
        "start_date": startdatum,
        "end_date": einddatum,
    }
    response = requests.get(eindpunt, params=params)
    if response.status_code == 200:
        data = response.json()
        pm10_metingen = [m for m in data['data'] if m['formula'] == 'PM10']
        return pm10_metingen
    else:
        logging.error(f"Probleem bij ophalen resultaten: {response.status_code}")
        return None

def haal_stations_op():
    eindpunt = f"{basisUrl}/stations"
    response = requests.get(eindpunt)
    if response.status_code == 200:
        return response.json()
    else:
        logging.error(f"Kan stations niet ophalen: {response.status_code}")
        return None

def maak_grafiek(metingen, station_naam):
    tijden = [datetime.strptime(m['timestamp_measured'], '%Y-%m-%dT%H:%M:%S%z').astimezone(timezone.utc) for m in metingen]
    waarden = [m['value'] for m in metingen]
    
    plt.figure(figsize=(10, 6))
    plt.plot(tijden, waarden, label='PM10')
    plt.xlabel('Tijd')
    plt.ylabel('PM10 Concentratie (µg/m³)')
    plt.title(f'PM10 Concentratie over Tijd bij Station {station_naam}')
    plt.legend()
    plt.grid(True)
    
    output_path = os.path.join(mapLocatie, f"PM10_{station_naam}.png")
    plt.savefig(output_path)
    plt.close()

if __name__ == "__main__":
    startdatum = "2023-05-15"
    einddatum = "2023-05-15"
    
    logging.info(f"Gegevens ophalen van {startdatum} tot {einddatum}")
    
    stations = haal_stations_op()
    
    if stations:
        for station in stations['data']:
            stationNummer = station['number']
            stationNaam = station['location']
            pm10_metingen = haal_fijnstofmetingen_op(stationNummer, startdatum, einddatum)
            
            if pm10_metingen:
                maak_grafiek(pm10_metingen, stationNaam)
            else:
                logging.info(f"Geen pm10 meetingen gevonden voor {stationNaam} ({stationNummer})")
    else:
        logging.info("Geen stations gevonden")
