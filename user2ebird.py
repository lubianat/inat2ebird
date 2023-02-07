from observation2ebird import *

from tqdm import tqdm

from pathlib import Path
import pandas as pd

HERE = Path(__file__).parent.resolve()


def main():
    try:
        user_id = sys.argv[1]
    except:
        user_id = input("Enter the iNaturalist user id:")

    save_all_observations_from_user(user_id, only_new_taxa=True)


def save_all_observations_from_user(user_id, only_new_taxa=False):
    date = "2022-10-15"
    url = (
        f"https://api.inaturalist.org/v1/observations?taxon_id=3&user_id={user_id}"
        f"&quality_grade=research&per_page=200&order=desc&order_by=observed_on"
    )

    r = requests.get(url)
    data = r.json()

    life_list_df = pd.read_csv(
        HERE.joinpath("ebird_world_life_list_tiago_lubiana_manual_download.csv")
    )
    life_list = [a.split(" - ")[1] for a in life_list_df["Species"]]
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
            with open("log.txt", "a") as f:
                f.write(f"Error '{e}' with entry {observation['id']}\n")
    filename = f"all_bird_entries_{user_id}_before_{date}.csv"
    with open(filename, "w", newline="\n") as f:
        writer = csv.writer(f)
        for entry in entries:
            write_row_for_entry(entry, writer)


if __name__ == "__main__":
    main()
