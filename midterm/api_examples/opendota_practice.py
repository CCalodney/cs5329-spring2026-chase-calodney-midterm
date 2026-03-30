#Examples of opendota api requests

import requests

BASE_URL = "https://api.opendota.com/api"

def get(endpoint, params=None):
    r = requests.get(f"{BASE_URL}/{endpoint}", params=params or {})
    r.raise_for_status()
    return r.json()

def get_heroes():
    return {h["id"]: h["localized_name"] for h in get("heroes")}

def get_public_matches(less_than_match_id=None):
    params = {}
    if less_than_match_id:
        params["less_than_match_id"] = less_than_match_id
    return get("publicMatches", params)

def get_match(match_id):
    return get(f"matches/{match_id}")

def get_hero_stats():
    return get("heroStats")

def get_pro_matches():
    return get("proMatches")


if __name__ == "__main__":
    import json

    heroes = get_heroes()
    print(f"{len(heroes)} heroes")

    matches = get_public_matches(less_than_match_id=8749000000)
    print(f"{len(matches)} public matches fetched")
    print(json.dumps(matches[0], indent=2))

    match = get_match(matches[0]["match_id"])
    print(f"\nmatch {match['match_id']} duration: {match['duration']}s")