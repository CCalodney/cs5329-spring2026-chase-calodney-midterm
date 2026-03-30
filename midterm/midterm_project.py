import json
import time
import tracemalloc
from itertools import combinations

# Must run collect_data.py first to get match data
def load_matches(filename):
    with open(filename) as f:
        matches = json.load(f)

    clean = []
    for m in matches:
        radiant = m["radiant_team"]
        dire = m["dire_team"]

        if 0 in radiant or 0 in dire:
            continue
        if len(radiant) != 5 or len(dire) != 5:
            continue

        has_dupes = False
        for team in [radiant, dire]:
            s = sorted(team)
            for i in range(len(s) - 1):
                if s[i] == s[i + 1]:
                    has_dupes = True
                    break
            if has_dupes:
                break
        if has_dupes:
            continue

        clean.append(m)

    return clean


######### Baseline: Linear Scan #########################

def linear_scan(matches, hero_ids, combo_size=2):
    target = tuple(sorted(hero_ids))
    total = 0
    wins = 0

    for match in matches:
        radiant = match["radiant_team"]
        dire = match["dire_team"]
        radiant_win = match["radiant_win"]

        for combo in combinations(sorted(radiant), combo_size):
            if combo == target:
                total += 1
                if radiant_win:
                    wins += 1
                break

        for combo in combinations(sorted(dire), combo_size):
            if combo == target:
                total += 1
                if not radiant_win:
                    wins += 1
                break

    if total == 0:
        return None
    return {"total": total, "wins": wins, "winrate": wins / total}


###### Optimized: Hash Table ###################

def build_index(matches, combo_size=2):
    index = {}

    for match in matches:
        radiant = match["radiant_team"]
        dire = match["dire_team"]
        radiant_win = match["radiant_win"]

        for combo in combinations(sorted(radiant), combo_size):
            if combo not in index:
                index[combo] = [0, 0]
            index[combo][0] += 1
            if radiant_win:
                index[combo][1] += 1

        for combo in combinations(sorted(dire), combo_size):
            if combo not in index:
                index[combo] = [0, 0]
            index[combo][0] += 1
            if not radiant_win:
                index[combo][1] += 1

    return index


def lookup(index, hero_ids):
    key = tuple(sorted(hero_ids))
    if key not in index:
        return None
    total, wins = index[key]
    return {"total": total, "wins": wins, "winrate": wins / total}


#################### Benchmarks   ######################################################

def benchmark_baseline(matches, queries, combo_size=2):
    times = []
    for q in queries:
        start = time.perf_counter()
        linear_scan(matches, q, combo_size)
        end = time.perf_counter()
        times.append(end - start)
    return times


def benchmark_hashtable(matches, queries, combo_size=2):
    tracemalloc.start()
    start = time.perf_counter()
    index = build_index(matches, combo_size)
    build_time = time.perf_counter() - start
    _, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    times = []
    for q in queries:
        start = time.perf_counter()
        lookup(index, q)
        end = time.perf_counter()
        times.append(end - start)

    return build_time, peak_mem, times


def run_benchmarks(filename, queries, combo_size=2):
    matches = load_matches(filename)
    print(f"\n{'========================================================================================================================'}")
    print(f"Dataset: {filename} ({len(matches)} matches)")
    print(f"Combo size: {combo_size}")
    print(f"Queries: {len(queries)}")
    print(f"\n{'========================================================================================================================'}")

    index = build_index(matches, combo_size)
    for q in queries:
        baseline_result = linear_scan(matches, q, combo_size)
        ht_result = lookup(index, q)
        if baseline_result != ht_result:
            print(f"MISMATCH")
            return
    print("PASSED")

    for q in queries:
        result = lookup(index, q)
        if result:
            print(f"  heroes {q}: {result['total']} games, {result['winrate']:.2%} winrate")
        else:
            print(f"  heroes {q}: no data")
    print("\n")
    baseline_times = benchmark_baseline(matches, queries, combo_size)

    baseline_times = benchmark_baseline(matches, queries, combo_size)
    avg_baseline_ms = sum(baseline_times) / len(baseline_times) * 1000
    avg_baseline_ms = round(avg_baseline_ms, 2)
    print(f"baseline avg query: {avg_baseline_ms} ms")

    build_time, peak_mem, ht_times = benchmark_hashtable(matches, queries, combo_size)
    build_ms = round(build_time * 1000, 2)
    mem_mb = round(peak_mem / 1024 / 1024, 2)
    avg_ht_ms = sum(ht_times) / len(ht_times) * 1000
    avg_ht_ms = round(avg_ht_ms, 4)
    print(f"hashtable build: {build_ms} ms")
    print(f"hashtable memory: {mem_mb} MB")
    print(f"hashtable avg query: {avg_ht_ms} ms")

    if avg_ht_ms > 0:
        speedup = round(avg_baseline_ms / avg_ht_ms, 1)
        print(f"speedup: {speedup}x")


if __name__ == "__main__":
    test_queries_pairs = [
        [14, 35],
        [22, 25],
        [1, 2],
        [50, 44],
        [27, 5],
    ]

    test_queries_triples = [
        [14, 35, 22],
        [1, 2, 5],
        [50, 44, 27],
    ]

    for f in ["matches_10k.json", "matches_100k.json", "matches_1m.json"]:
        run_benchmarks(f, test_queries_pairs, combo_size=2)

    for f in ["matches_10k.json", "matches_100k.json", "matches_1m.json"]:
        run_benchmarks(f, test_queries_triples, combo_size=3)