#!/usr/bin/env python3
import requests
import urllib.parse
import sys
import time
from datetime import datetime
from dataclasses import dataclass
import dataclasses
import pandas as pd
import csv
import os 

name: str
unit_price: float
quantity_on_hand: int = 0

country_dict = {"Brasil": "BR", "Espanha": "ES"}

import os

from ebird.api.requests import get_observations

# It is a good idea to store secrets in environment variables 
# (but if you don't commit, you can add it as a string here too)
EBIRD_API_KEY = os.environ["EBIRD_API_KEY"]

@dataclass
class eBirdEntry:
    """Class for formatting an iNaturalist entry to eBird."""

    genus: str
    species: str
    location: str
    latitude: str
    longitude: str
    date: str
    start_time: str
    state_province: str
    country_code: str
    common_name: str = ""
    number: str = "X"  # The number of birds seen there as string (defaults to 'X')
    species_comments: str = ""
    protocol: str = "Incidental"
    number_of_observers: int = 1
    duration: int = 0
    all_observations_reported: bool = False
    effort_distance_miles: int = 0
    effort_area_acres: int = 0
    submission_comments: str = ""


def main():
    try:
        inaturalist_id = sys.argv[1]
    except:
        inaturalist_id = input("Enter the iNaturalist observation id:")

    entry = generate_entry_from_id(inaturalist_id, EBIRD_API_KEY)
    filename = "items.csv"
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        write_row_for_entry(entry, writer)


def write_row_for_entry(entry, writer):
    writer.writerow(
        [
            entry.common_name,
            entry.genus,
            entry.species,
            entry.number,
            entry.species_comments,
            entry.location,
            entry.latitude,
            entry.longitude,
            entry.date,
            entry.start_time,
            entry.state_province,
            entry.country_code,
            entry.protocol,
            entry.number_of_observers,
            entry.duration,
            entry.all_observations_reported,
            entry.effort_distance_miles,
            entry.effort_area_acres,
            entry.submission_comments,
        ]
    )


def generate_entry_from_id(inaturalist_id, EBIRD_API_KEY):
    base_url = "https://api.inaturalist.org/v1/"
    observation_url = base_url + f"observations/{inaturalist_id}"

    result = requests.get(observation_url)
    data = result.json()
    observation_data = data["results"][0]
    entry = generate_entry_from_observation_data(observation_data, EBIRD_API_KEY)

    return entry


def generate_entry_from_observation_data(observation_data, EBIRD_API_KEY=EBIRD_API_KEY):
    inaturalist_id = observation_data["id"]
    date_inat = observation_data["time_observed_at"][:-6]  # Remove time zone
    date = datetime.strptime(date_inat, "%Y-%m-%dT%H:%M:%S")

    date_ebird = date.strftime("%m/%d/%Y")
    start_time_ebird = date.strftime("%H:%M")
    location_string = observation_data["place_guess"]

    latitude = observation_data["location"].split(",")[0]
    longitude = observation_data["location"].split(",")[1]
    taxon_data = observation_data["taxon"]
    location_url = (
        f"https://api.ebird.org/v2/ref/hotspot/geo?lat={latitude}&lng={longitude}"
    )
    location_guess = requests.get(
        location_url, headers={"X-eBirdApiToken": EBIRD_API_KEY}
    )
    country_code = location_guess.text.split(",")[1]
    regional_code = location_guess.text.split(",")[2].split("-")[1]
    species = taxon_data["name"]
    genus = species.split(" ")[0]
    entry = eBirdEntry(
        genus=genus,
        species=species.split(" ")[-1],
        location=location_string,
        latitude=latitude,
        longitude=longitude,
        date=date_ebird,
        start_time=start_time_ebird,
        state_province=regional_code,
        country_code=country_code,
        submission_comments=f"iNaturalist observation https://www.inaturalist.org/observations/{inaturalist_id}",
    )

    return entry


if __name__ == "__main__":
    main()
