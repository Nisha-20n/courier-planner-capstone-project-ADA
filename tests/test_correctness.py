"""
test_correctness.py  --  Correctness evidence (Phase 4)

Har algorithm ko ek "slow but obviously correct" method se compare karte hain:
  - Merge sort        vs Python's sorted()
  - Knapsack DP       vs brute force (try every subset)
  - Dijkstra          vs Bellman-Ford
  - Route (NN, 2-opt) vs brute-force optimal route (small inputs)

Run:  python tests/test_correctness.py
"""

import itertools
import os
import random
import sys

# Allow "from algorithms..." when this file is run from any folder
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algorithms.sorting import merge_sort
from algorithms.knapsack import knapsack
from algorithms.graph import Graph
from algorithms.tsp import (build_distance_table, nearest_neighbour,
                            two_opt, route_length)


# ---------------------------------------------------------------- helpers
def random_graph(num_nodes, rng):
    """Connected random graph. Node names: Depot, L1, L2, ..."""
    names = ["Depot"] + [f"L{i}" for i in range(1, num_nodes)]
    g = Graph()
    for i in range(1, num_nodes):                       # spanning tree = connected
        g.add_edge(names[i], names[rng.randrange(i)], rng.randint(1, 20))
    for _ in range(num_nodes):                          # a few extra roads
        a, b = rng.sample(names, 2)
        g.add_edge(a, b, rng.randint(1, 20))
    return g, names


def bellman_ford(graph, source):
    dist = {n: float("inf") for n in graph.adj}
    dist[source] = 0
    for _ in range(len(graph.adj) - 1):
        for u in graph.adj:
            for v, w in graph.adj[u]:
                if dist[u] + w < dist[v]:
                    dist[v] = dist[u] + w
    return dist


def brute_force_knapsack(parcels, capacity):
    best = 0
    for r in range(len(parcels) + 1):
        for combo in itertools.combinations(parcels, r):
            if sum(p["weight"] for p in combo) <= capacity:
                best = max(best, sum(p["value"] for p in combo))
    return best


def brute_force_route(depot, stops, table):
    best = float("inf")
    for perm in itertools.permutations(stops):
        route = [depot] + list(perm) + [depot]
        best = min(best, route_length(route, table))
    return best


# ------------------------------------------------------------------ tests
def test_sorting():
    rng = random.Random(1)
    for _ in range(200):
        data = [rng.randint(0, 50) for _ in range(rng.randint(0, 40))]
        assert merge_sort(data) == sorted(data)
        assert merge_sort(data, reverse=True) == sorted(data, reverse=True)
    # stability: equal keys keep their original order
    items = [("a", 1), ("b", 1), ("c", 0), ("d", 1)]
    assert [x[0] for x in merge_sort(items, key=lambda x: x[1])] == ["c", "a", "b", "d"]
    print("PASS  merge sort matches sorted() on 200 random lists (and is stable)")


def test_knapsack():
    rng = random.Random(2)
    for _ in range(200):
        n = rng.randint(1, 10)
        parcels = [{"id": f"P{i}", "weight": rng.randint(1, 10),
                    "value": rng.randint(1, 100)} for i in range(n)]
        capacity = rng.randint(1, 30)
        value, chosen = knapsack(parcels, capacity)
        assert value == brute_force_knapsack(parcels, capacity)
        assert sum(p["weight"] for p in chosen) <= capacity
        assert sum(p["value"] for p in chosen) == value
    print("PASS  knapsack DP equals brute force on 200 random cases")


def test_dijkstra():
    rng = random.Random(3)
    for _ in range(100):
        g, names = random_graph(rng.randint(3, 15), rng)
        dist, _ = g.dijkstra("Depot")
        assert dist == bellman_ford(g, "Depot")
    print("PASS  Dijkstra equals Bellman-Ford on 100 random graphs")


def test_route():
    rng = random.Random(4)
    worst_nn = worst_2opt = 1.0
    for _ in range(60):
        k = rng.randint(3, 7)                           # stops (brute force limit)
        g, names = random_graph(k + 1, rng)
        stops = names[1:]
        table = build_distance_table(g, names)

        nn = nearest_neighbour("Depot", stops, table)
        opt2 = two_opt(nn, table)
        best = brute_force_route("Depot", stops, table)

        for route in (nn, opt2):                        # valid round trip
            assert route[0] == route[-1] == "Depot"
            assert sorted(route[1:-1]) == sorted(stops)
        assert route_length(opt2, table) <= route_length(nn, table)
        assert route_length(opt2, table) >= best

        worst_nn = max(worst_nn, route_length(nn, table) / best)
        worst_2opt = max(worst_2opt, route_length(opt2, table) / best)
    print("PASS  routes are valid round trips; 2-opt never worse than nearest neighbour")
    print(f"      worst length vs optimal (60 cases, 3-7 stops): "
          f"nearest neighbour x{worst_nn:.2f}, with 2-opt x{worst_2opt:.2f}")


if __name__ == "__main__":
    test_sorting()
    test_knapsack()
    test_dijkstra()
    test_route()
    print("\nAll correctness tests passed.")
