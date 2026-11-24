# Intelligent Courier Planning System (Capstone)

A Python prototype that, given parcels and delivery points, produces an
**optimized packing plan** and an **ordered delivery route**. It integrates
sorting, dynamic programming, graph algorithms and approximation.

## Project structure
```
courier_project/
├── main.py                    planner (run this)
├── benchmark.py               runtime experiments, writes results/
├── requirements.txt           matplotlib (only needed for charts)
├── algorithms/
│   ├── sorting.py             merge sort
│   ├── knapsack.py            0/1 knapsack (dynamic programming)
│   ├── graph.py               weighted graph + Dijkstra
│   └── tsp.py                 nearest neighbour + 2-opt
├── data/
│   ├── input.json             sample parcels, roads, capacity
│   └── sample_output.txt      output of: python main.py --show-dp
├── tests/
│   └── test_correctness.py    checks each algorithm against a slow, obviously correct method
├── results/                   benchmark CSVs, charts, test output
└── docs/
    ├── DESIGN.md              Phase 1: problem design and planning
    └── REPORT.md              Phases 4-5: testing, results, report
```

## Algorithms

| Topic | File | Technique | Time complexity |
|---|---|---|---|
| Sorting | `algorithms/sorting.py` | Merge sort (by priority, then value) | O(n log n) |
| Dynamic programming | `algorithms/knapsack.py` | 0/1 knapsack | O(n * W) |
| Graph algorithms | `algorithms/graph.py` | Dijkstra with a min-heap | O((V + E) log V) |
| Approximation | `algorithms/tsp.py` | Nearest neighbour, then 2-opt | NN: O(k^2); 2-opt: O(k^3) per pass as written |

n = parcels, W = van capacity, V/E = locations/roads, k = stops in a trip.
The exact route (TSP) is NP-hard, so a heuristic is used.

## How it works
1. Read `data/input.json`.
2. Sort parcels with merge sort (priority high to low, then value).
3. Run knapsack DP on the remaining parcels to choose one van load.
4. Build the road graph; Dijkstra gives shortest distances between stops.
5. Plan the route (nearest neighbour, improved with 2-opt), starting and ending at the depot.
6. Repeat from step 3 until all deliverable parcels are assigned to trips.
   Parcels that are too heavy or have no road are reported as not delivered.

## Run
Requires Python 3.8+. The planner and tests need no extra packages.

```
python main.py                      # plan trips for data/input.json
python main.py --show-dp            # also print the DP table
python main.py my_input.json        # use another input file
python tests/test_correctness.py    # correctness tests
pip install -r requirements.txt     # only for benchmark charts
python benchmark.py                 # runtime tables and charts in results/
```

## Input format (`data/input.json`)
- `depot`: starting location name
- `capacity`: van capacity in kg (integer)
- `parcels`: list of `{id, weight (int), value, priority (higher = more urgent), destination}`
- `roads`: list of `[location1, location2, distance_km]` (two-way roads)

## Sample result
The included sample gives 3 trips and a total distance of 100 km
(see `data/sample_output.txt`).

## Testing and performance
- `tests/test_correctness.py` compares merge sort with `sorted()`, knapsack with brute
  force, Dijkstra with Bellman-Ford, and routes with the brute-force optimum on small inputs.
- `benchmark.py` times each step for 10 to 2000 parcels and 5 to 120 stops.
  Results, charts and optimization comments are in `docs/REPORT.md`.

## Limitations
- Weights must be integers (needed for the DP table).
- The route is an approximation, not guaranteed to be the shortest possible.
- Packing is greedy across trips (best load first), not globally optimal.
