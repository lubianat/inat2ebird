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


def save_all_observations_from_user(
    user_id,
    only_new_taxa=False,
    path_to_life_list="ebird_world_life_list.csv",
    EBIRD_API_KEY=EBIRD_API_KEY,
    base_dir=HERE,
):
    data = fetch_inaturalist_data(user_id)
    life_list = load_ebird_life_list(path_to_life_list)

    entries = generate_entries(
        data, life_list, only_new_taxa, EBIRD_API_KEY=EBIRD_API_KEY
    )
    write_entries_to_csv(entries, user_id, base_dir=base_dir)


def fetch_inaturalist_data(user_id):
    url = f"https://api.inaturalist.org/v1/observations?taxon_id=3&user_id={user_id}&quality_grade=research&per_page=200&order=desc&order_by=observed_on"
    response = requests.get(url)
    return response.json()


def load_ebird_life_list(path_to_list="ebird_world_life_list.csv"):
    life_list_df = pd.read_csv(HERE.joinpath(path_to_list))
    return [a for a in life_list_df["Scientific Name"]]


def generate_entries(data, life_list, only_new_taxa, EBIRD_API_KEY=EBIRD_API_KEY):
    entries = []
    for observation in tqdm(data["results"]):
        species = observation["taxon"]["name"]
        if only_new_taxa and species in life_list:
            continue
        try:
            life_list.append(species)
            entry = generate_entry_from_observation_data(
                observation, EBIRD_API_KEY=EBIRD_API_KEY
            )
            entries.append(entry)
        except Exception as e:
            print(e)
            log_error(e, observation)
    return entries


def log_error(error, observation):
    with open("log.txt", "a") as f:
        f.write(f"Error '{error}' with entry {observation['id']}\n")


def write_entries_to_csv(entries, user_id, base_dir=HERE):
    filename = f"all_bird_entries_{user_id}.csv"
    with open(filename, "w", newline="\n") as f:
        writer = csv.writer(f)
        for entry in entries:
            write_row_for_entry(entry, writer)


if __name__ == "__main__":
    print(
        "Make sure you download your life list from https://ebird.org/lifelist?time=life&r=world as 'ebird_world_life_list.csv'"
    )

    print(
        "Also make sure you get add to observation2ebird your valid eBird API key (https://ebird.org/api/keygen)"
    )
    main()
    print(
        "Your new entries have been parsed into a spreadsheet! Upload it in the ebird record format at https://ebird.org/import/upload.form?theme=ebird."
    )
