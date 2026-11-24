# Phase 1: Courier Problem Design and Planning

## 1. Problem statement
A courier van starts at a depot with a list of parcels. The van can carry only a
limited weight, so not every parcel fits in one trip. The system must decide:

1. **Which parcels go on each trip** (maximize the total value carried, within the van's capacity).
2. **In what order to visit the delivery points** so the van travels a short distance and returns to the depot.

## 2. Data design

### Parcel attributes
| Attribute | Type | Meaning |
|---|---|---|
| `id` | text | Unique parcel name (P1, P2, ...) |
| `weight` | integer (kg) | Space used in the van. Integer is required by the DP table |
| `value` | number | Importance/revenue of delivering the parcel (what knapsack maximizes) |
| `priority` | integer 1-3 | 3 = most urgent. Used for sorting |
| `destination` | text | Delivery point (a graph node) |

### Delivery points and roads (graph format)
- **Node** = a location (`Depot`, `A`, `B`, ...).
- **Edge** = a two-way road with a distance in km.
- Stored as an **adjacency list**: `{node: [(neighbour, distance), ...]}`. This is
  efficient for sparse road networks (O(V + E) memory).

### Input file (`data/input.json`)
```
{ "depot": "Depot", "capacity": 15,
  "parcels": [ {"id": "P1", "weight": 5, "value": 60, "priority": 2, "destination": "A"}, ... ],
  "roads":   [ ["Depot", "A", 4], ["A", "B", 3], ... ] }
```

## 3. Algorithm selection

| Sub-problem | Algorithm | Why this one |
|---|---|---|
| Order parcels by priority | **Merge sort** | Guaranteed O(n log n) in every case, and stable (equal items keep their order), unlike quicksort's O(n^2) worst case |
| Choose parcels for one trip | **0/1 knapsack, Dynamic Programming** | Each parcel is taken whole or not at all. Greedy by value/weight can be wrong; DP is exact. O(n * capacity) |
| Distances between delivery points | **Dijkstra (min-heap)** | Road distances are non-negative; Dijkstra gives exact shortest paths in O((V+E) log V) |
| Order of delivery stops | **Nearest neighbour (TSP approximation)**, improved by **2-opt** | The exact route is the Travelling Salesman Problem (NP-hard, O(k!) to check all orders). Nearest neighbour is fast (O(k^2)); 2-opt then removes crossings to shorten the route |

## 4. How the parts work together

```
 input.json
     |
     v
 [1] Read parcels, roads, capacity
     |
     v
 [2] MERGE SORT parcels (priority high -> low, then value)
     |
     v
 +-> [3] KNAPSACK DP on remaining parcels -> parcels for this trip
 |        |
 |        v
 |   [4] Collect the trip's destinations (stops)
 |        |
 |        v
 |   [5] DIJKSTRA from depot and every stop -> distance table
 |        |
 |        v
 |   [6] NEAREST NEIGHBOUR order, then 2-OPT improvement -> route
 |        |
 |        v
 |   [7] Print packing plan, route, road path, distance
 |        |
 +--------+  repeat while parcels remain (next trip)
```

Parcels that are heavier than the van, or whose destination has no road from the
depot, are reported as "not delivered" instead of crashing the program.

## 5. Design decisions and assumptions
- Distances are in km and roads are two-way.
- The van returns to the depot at the end of each trip.
- Value and priority are separate: knapsack maximizes **value**; **priority**
  decides the order of the sorted list (and breaks ties in packing).
- Trips are planned greedily: the best possible load first, then the best load
  from what remains. This is simple and explainable, but not guaranteed to give
  the minimum number of trips overall.
- The route is an approximation, so it may not be the shortest possible.
  `tests/test_correctness.py` measures how far off it is on small cases.
