import requests
import json
import time

BASE_URL = "https://api.opendota.com/api"
BATCH_SIZE = 50000

def fetch_batch(max_id=None):
    sql = "SELECT match_id, radiant_win, radiant_team, dire_team FROM public_matches WHERE duration > 300"
    if max_id:
        sql += f" AND match_id < {max_id}"
    sql += f" ORDER BY match_id DESC LIMIT {BATCH_SIZE}"

    r = requests.get(f"{BASE_URL}/explorer", params={"sql": sql})
    data = r.json()
    return data.get("rows", [])


def collect(target):
    matches = []
    last_id = None

    while len(matches) < target:
        batch = fetch_batch(last_id)
        if not batch:
            break
        matches += batch
        last_id = batch[-1]["match_id"]
        print(f"{len(matches)}")

    return matches[:target]

def save(matches, filename):
    with open(filename, "w") as f:
        json.dump(matches, f)
    print(f"Saved {len(matches)} matches to {filename}")

if __name__ == "__main__":
    print("\n10k")
    data_10k = collect(10000)
    save(data_10k, "matches_10k.json")

    print("\n100k")
    data_100k = collect(100000)
    save(data_100k, "matches_100k.json")

    print("\n1m")
    data_1m = collect(1000000)
    save(data_1m, "matches_1m.json")
    print("\nDONE.")