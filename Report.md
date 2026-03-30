## Analytical Report: Efficient Win Rate Lookup for Dota Hero Combinations Using Hash Tables

## 1. Introduction

A common problem in computer science is efficiently finding patterns within large datasets. Scanning significantly large enough datasets done with a naive approach can take a significant amount of time, increasing the need for optimized approaches. One method is using hash tables to separate and store desired collections of data, so that future lookups will all be O(1). A great way to apply this is using games, which have hidden within their data many significant statistics that players would find incredibly helpful. Dota 2 is a competitive multiplayer game with millions of public matches available through the OpenDota API. This project takes that match data and compares a baseline linear scan against an optimized hash table approach for looking up win rates of specific hero combinations — pairs or triples of heroes that appeared on the same team. The goal is to stay under 100ms average query time and under 1 GB of memory.

## 2. Dataset

Match data was collected from the OpenDota API using their SQL endpoint, which allows direct SQL queries on their database. I collected three datasets of increasing size: 10K, 100K, and 1M matches. Each match record contains four fields: match_id, radiant_win, radiant_team (a list of 5 hero IDs), and dire_team (also a list of 5 hero IDs). All of this data is saved and stored locally in json files.

I filter out some matches to try and avoid any bad or unwanted data. For example, any matches less than 5 minutes long are excluded, because this typically means someone left the match, making the data undesirable. I also filter out matches where a hero ID is 0(unknown hero), matches where either team doesn't have exactly 5 heroes(impossible), and matches with duplicate heroes on the same team(also impossible). These are all signs of corrupted or incomplete data that would throw off the results. After filtering, the datasets contain 9,995, 99,954, and 999,392 valid matches respectively. The vast majority of matches pass filtering without issue. 

## 3. Approach A: Baseline Linear Scan
The baseline approach scans through every match in the dataset each time a query is made. For a given set of hero IDs, it generates all combinations of that size from each team in each match and checks for a match. If the combination is found, it records whether that team won or lost.
This is O(N) per query where N is the number of matches. There is no preprocessing step and no additional memory usage beyond the dataset itself. It is the simplest possible approach and serves as the correctness reference for the optimized method.

## 4. Approach B: Hash Table
The optimized approach preprocesses the entire dataset into a hash table. For every match, it generates all 2-hero or 3-hero combinations from each team and inserts them as keys in the dictionary. Each key maps to a list tracking total games and total wins for that combination.
Preprocessing is O(N) where N is the number of matches, since each match generates a fixed number of combinations (C(5,2) = 10 pairs per team, or C(5,3) = 10 triples per team). After the index is built, any query is a single dictionary lookup O(1). The space complexity is O(k) where k is the number of unique hero combinations that appear in the data.

## 5. Benchmark Results

### Pairs

| Dataset | Baseline Avg | HT Build | HT Query | Memory | Speedup |
|---------|-------------|----------|----------|--------|---------|
| 10K | 9.45 ms | 67.54 ms | 0.001 ms | 1.32 MB | 9,450x |
| 100K | 96.32 ms | 717.35 ms | 0.0013 ms | 1.42 MB | 74,092x |
| 1M | 962.47 ms | 9,453 ms | 0.0011 ms | 1.78 MB | 874,973x |

### Triples

| Dataset | Baseline Avg | HT Build | HT Query | Memory | Speedup |
|---------|-------------|----------|----------|--------|---------|
| 10K | 9.98 ms | 153.32 ms | 0.0028 ms | 20.25 MB | 3,564x |
| 100K | 99.15 ms | 1,122 ms | 0.0036 ms | 49.18 MB | 27,542x |
| 1M | 1,009 ms | 14,711 ms | 0.0074 ms | 56.17 MB | 136,404x |

## 6. Analysis
The basline scales linearly with dataset size exactly as you'd expect. As the data set increases by 10x, so does the query time. At 1M matches, the baseline goes over the 100ms query time target.

The hash table query time stays very similar, regardless of the dataset size, never going higher than 0.074 ms. This is expected O(1) behavior. One
downside is the build time for the hash table, being 14,711 ms for three hero combinations and 1M match dataset. However, when considering that this is a one time build, and every query afterwards will be around 0.001ms, that time is quickly made up for. Memory is also another potential issue. For pairs of heroes, the size is C(127,2) = 8001 possible hero pairs. For triples, it's 333,375 possible combinations. If you wanted to see the winrate of a specific, full team, it'd be over 200 million. This is the main reason why I only checked pairs and trios, and is something to consider when choosing to use a hash table. However, for the scope of this project, when checking combinations of two or 3 heroes, the memory usage isn't significant enough to cause any issues and is well below the 1GB maximum I gave myself.


## 7. Conclusion
The hash table approach meets both project constraints with room to spare. Query times are well under 100ms and memory usage peaks at 56 MB, far below the 1 GB budget. The baseline is adequate for small datasets or single queries, but it fails the 100ms target at 1M matches and would only get worse with more data.
The baseline is in all cases significantly slower than the hash table for lookup as expected. While the build time for the hash table may look significant, it is easily overtaken by the baseline average as the number of queries increases. For a use case like analyzing Dota hero combinations where users are likely to make many queries against the same dataset, the hash table is the right choice.
