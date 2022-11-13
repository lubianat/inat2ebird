#!/usr/bin/env python3
import requests
import urllib.parse
import sys
import time
from datetime import datetime
from dataclasses import dataclass
import pandas as pd
import csv

name: str
unit_price: float
quantity_on_hand: int = 0


@dataclass
class eBirdEntry:
    """Class for formatting an iNaturalist entry to eBird."""

    common_name: str
    genus: str
    species: str
    location: str
    latitude: str
    longitude: str
    date: str
    state_province: str
    country_code: str
    number: int = 0  # The number of birds seen there
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

    base_url = "https://api.inaturalist.org/v1/"
    observation_url = base_url + f"observations/{inaturalist_id}"

    result = requests.get(observation_url)
    data = result.json()
    observation_data = data["results"][0]
    date_inat = observation_data["time_observed_at"].split("+")[0]
    date = datetime.strptime(date_inat, "%Y-%m-%dT%H:%M:%S")

    date_ebird = date.strftime("%Y/%m/%d")
    start_time_ebird = date.strftime("%H:%M")
    location_string = observation_data["place_guess"]

    latitude = observation_data["location"].split(",")[0]
    longitude = observation_data["location"].split(",")[1]
    taxon_data = observation_data["taxon"]

    common_name = taxon_data["preferred_common_name"]
    species = taxon_data["name"]
    genus = species.split(" ")[0]
    entry = eBirdEntry(
        common_name=common_name,
        genus=genus,
        species=species,
        location=location_string,
        latitude=latitude,
        longitude=longitude,
        date=date_ebird,
        state_province=location_string,
        country_code=location_string,
    )
    df = pd.DataFrame(entry)
    filename = "items.csv"
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        for item in items:
            writer.writerow([item.id, item.name, item.category])


if __name__ == "__main__":
    main()