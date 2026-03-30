# Midterm Project - Efficient Win Rate Lookup for Dota Hero Combinations Using Hash Tables

**Course:** CS 5329 – Algorithm Design and Analysis  
**Student Name:** Chase Calodney 
**Semester:** Spring 2026

---

## Overview
This project compares a baseline linear scan against an optimized hash table approach for looking up win rates of multi-hero combinations in Dota 2. Match data is collected from the OpenDota API using their explorer SQL endpoint and saved locally as JSON files. The baseline approach scans through every match per query (O(N)), while the optimized approach preprocesses all hero combinations into a hash table for O(1) lookup.

---

## How to Run the Code
From the repository directory, run:

```bash
pip install -r requirements.txt
```
Then to collect match data, run:
python collect_data.py

Finally, to run benchmarks:
python midterm_project.py

## Output(w/ improved formatting)

Benchmark Results
=================

### Pairs (combo size = 2)

| Dataset | Baseline Avg | HT Build | HT Query | Memory | Speedup |
|---------|-------------|----------|----------|--------|---------|
| 10K | 9.45 ms | 67.54 ms | 0.001 ms | 1.32 MB | 9,450x |
| 100K | 96.32 ms | 717.35 ms | 0.0013 ms | 1.42 MB | 74,092x |
| 1M | 962.47 ms | 9,453 ms | 0.0011 ms | 1.78 MB | 874,973x |

### Triples (combo size = 3)

| Dataset | Baseline Avg | HT Build | HT Query | Memory | Speedup |
|---------|-------------|----------|----------|--------|---------|
| 10K | 9.98 ms | 153.32 ms | 0.0028 ms | 20.25 MB | 3,564x |
| 100K | 99.15 ms | 1,122 ms | 0.0036 ms | 49.18 MB | 27,542x |
| 1M | 1,009 ms | 14,711 ms | 0.0074 ms | 56.17 MB | 136,404x |

## Results Summary
The hash table implementation demonstrates a massive performance improvement over the baseline linear scan, easily meeting my sub-100ms query time goal. The baseline scales linearly with dataset size as expected from O(N), while the hash table lookup remains effectively constant at O(1) regardless of dataset size. You can actually see the baseline average increasing by 10x each time the dataset increases by that same amount, going from 9.45 to 96.32, to finally 962.47, behaving exactly how you'd expect a O(N) algorithm to. Memory usage stays well under the 1 GB budget even at 1 million matches. The tradeoff is the one-time preprocessing cost. Building the hash table for 1 million matches takes about 9.5 seconds for pairs and 14.7 seconds for triples, but once built, every query is nearly instant. In this way, it's hardly a tradeoff, since the baseline avg is what every query will take.

## Dataset
This project uses the OpenDota data set, which gives me access to millions of games through their API. When running collect_data.py, it will grab the most recent number of games for 10k, 100k, and 1M, so each time it's collected the dataset should be different. These batches of data are kept in their own files and used individually for the benchmark. I ran into some bad data issues, so I try to filter out any data coming in that would cause any issues. For example, in any given game of Dota 2, there must be 5 heroes on each team. If there is ever a match that doesn't have 5 heroes on both teams, something is wrong and the data must be ignored. Same applied for hero ID of 0 and duplicate heroes on same team.

