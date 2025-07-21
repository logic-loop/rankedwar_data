import requests
import typing
import json
import os
import pandas as pd
import random
import time
from tqdm import tqdm
from dotenv import load_dotenv

#make a .env text file with TORN_API_KEY=your_api_key_here
# and place it in the same or any parent directory of this script
load_dotenv()
API_KEY = os.getenv("TORN_API_KEY")


def get_ranked_war_report(war_id: int) -> typing.Dict[str, typing.Any]:
    url = f"https://api.torn.com/v2/faction/{war_id}/rankedwarreport"

    headers = {"accept": "application/json", "Authorization": f"ApiKey {API_KEY}"}

    response = requests.get(url, headers=headers)
    return response.json()


def load_data() -> typing.Dict[int, typing.Any]:
    """Load existing data from data.json if it exists."""
    if os.path.exists("data.json"):
        with open("data.json", "r") as f:
            return json.load(
                f,
                object_hook=lambda d: {
                    int(k) if k.isdigit() else k: v for k, v in d.items()
                },
            )
    return {}


if __name__ == "__main__":
    MIN_NUM = 18110
    MAX_NUM = 28110
    SAMPLE_SIZE = 100

    print("Starting up...")

    # Load existing data
    data = load_data()
    print(f"Loaded {len(data)} existing war reports")

    # Generate war IDs that haven't been processed yet
    existing_ids = set(data.keys())
    available_ids = list(set(range(MIN_NUM, MAX_NUM + 1)) - existing_ids)

    if len(available_ids) < SAMPLE_SIZE:
        print(f"Warning: Only {len(available_ids)} IDs available for sampling")
        sample_ids = available_ids
    else:
        sample_ids = random.sample(available_ids, SAMPLE_SIZE)

    # Fetch new war reports
    try:
        for war_id in tqdm(sample_ids, desc="Fetching war reports"):
            war_report = get_ranked_war_report(war_id)
            data[war_id] = war_report
            time.sleep(0.25)  # Wait 500ms between requests
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
    finally:
        with open("data.json", "w") as f:
            json.dump(data, f, indent=2)
        print(f"Saved {len(data)} war reports to data.json")
