import sys
import csv
import requests
import pandas as pd
from pathlib import Path
from tqdm import tqdm
from observation2ebird import *

# Set the current directory
HERE = Path(__file__).parent.resolve()


def main():
    user_id = get_user_id()
    save_all_observations_from_user(user_id, only_new_taxa=True)


def get_user_id():
    try:
        return sys.argv[1]
    except:
        return input("Enter the iNaturalist user id:")


def save_all_observations_from_user(user_id, only_new_taxa=False):
    data = fetch_inaturalist_data(user_id)
    life_list = load_ebird_life_list()

    entries = generate_entries(data, life_list, only_new_taxa)
    write_entries_to_csv(entries, user_id)


def fetch_inaturalist_data(user_id):
    url = f"https://api.inaturalist.org/v1/observations?taxon_id=3&user_id={user_id}&quality_grade=research&per_page=200&order=desc&order_by=observed_on"
    response = requests.get(url)
    return response.json()


def load_ebird_life_list():
    life_list_df = pd.read_csv(
        HERE.joinpath("ebird_world_life_list_tiago_lubiana_manual_download.csv")
    )
    return [a.split(" - ")[1] for a in life_list_df["Species"]]


def generate_entries(data, life_list, only_new_taxa):
    entries = []
    for observation in tqdm(data["results"]):
        species = observation["taxon"]["name"]
        if only_new_taxa and species in life_list:
            continue
        try:
            life_list.append(species)
            entry = generate_entry_from_observation_data(observation)
            entries.append(entry)
        except Exception as e:
            log_error(e, observation)
    return entries


def log_error(error, observation):
    with open("log.txt", "a") as f:
        f.write(f"Error '{error}' with entry {observation['id']}\n")


def write_entries_to_csv(entries, user_id):
    filename = f"all_bird_entries_{user_id}.csv"
    with open(filename, "w", newline="\n") as f:
        writer = csv.writer(f)
        for entry in entries:
            write_row_for_entry(entry, writer)


if __name__ == "__main__":
    main()
