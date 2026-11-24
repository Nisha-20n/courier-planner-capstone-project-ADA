"""
benchmark.py  --  Performance testing (Phase 4)

Do experiments chalte hain:

  Experiment A: poora pipeline, parcels ki sankhya badhate hue
                (10 ... 2000 parcels). Har step ka time naapte hain:
                sorting, knapsack DP, Dijkstra, nearest neighbour.

  Experiment B: sirf route planning, delivery stops badhate hue
                (5 ... 120 stops). Nearest neighbour vs 2-opt ka time aur
                route length compare karte hain.

Output: results/ folder mein CSV files aur PNG charts.

Run:  python benchmark.py
(Charts ke liye:  pip install matplotlib)
"""

import csv
import os
import random
import time

from algorithms.sorting import merge_sort
from algorithms.knapsack import knapsack
from algorithms.graph import Graph
from algorithms.tsp import (build_distance_table, nearest_neighbour,
                            two_opt, route_length)

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
CAPACITY = 200
REPEATS = 3          # har step 3 baar chalao, sabse kam time lo (noise kam hota hai)


# ------------------------------------------------------------ data makers
def make_graph(num_locations, rng):
    names = ["Depot"] + [f"L{i}" for i in range(1, num_locations)]
    g = Graph()
    for i in range(1, num_locations):                   # spanning tree: connected
        g.add_edge(names[i], names[rng.randrange(i)], rng.randint(1, 20))
    for _ in range(num_locations * 2):                  # extra roads
        a, b = rng.sample(names, 2)
        g.add_edge(a, b, rng.randint(1, 20))
    return g, names


def make_parcels(n, locations, rng):
    return [{"id": f"P{i}", "weight": rng.randint(1, 20), "value": rng.randint(10, 200),
             "priority": rng.randint(1, 3), "destination": rng.choice(locations[1:])}
            for i in range(n)]


def timed(fn, *args, **kwargs):
    """Return (result, best_time_in_ms) over REPEATS runs."""
    best = float("inf")
    result = None
    for _ in range(REPEATS):
        start = time.perf_counter()
        result = fn(*args, **kwargs)
        best = min(best, (time.perf_counter() - start) * 1000)
    return result, best


# ------------------------------------------------------------ experiments
def experiment_pipeline():
    rng = random.Random(42)
    rows = []
    for n in [10, 50, 100, 250, 500, 1000, 2000]:
        locations = max(10, n // 2)
        graph, names = make_graph(locations, rng)
        parcels = make_parcels(n, names, rng)

        sorted_parcels, t_sort = timed(
            merge_sort, parcels, key=lambda p: (p["priority"], p["value"]), reverse=True)
        (value, chosen), t_dp = timed(knapsack, sorted_parcels, CAPACITY)

        stops = sorted({p["destination"] for p in chosen})
        table, t_dij = timed(build_distance_table, graph, ["Depot"] + stops)
        _, t_nn = timed(nearest_neighbour, "Depot", stops, table)

        rows.append({"parcels": n, "locations": locations, "stops_in_trip": len(stops),
                     "sort_ms": t_sort, "knapsack_ms": t_dp,
                     "dijkstra_ms": t_dij, "nearest_neighbour_ms": t_nn})
    return rows


def experiment_route():
    rng = random.Random(7)
    rows = []
    for k in [5, 10, 20, 40, 80, 120]:
        graph, names = make_graph(k + 1, rng)
        stops = names[1:]
        table, t_dij = timed(build_distance_table, graph, names)
        nn, t_nn = timed(nearest_neighbour, "Depot", stops, table)
        improved, t_2opt = timed(two_opt, nn, table)
        len_nn = route_length(nn, table)
        len_2opt = route_length(improved, table)
        rows.append({"stops": k, "dijkstra_ms": t_dij, "nearest_neighbour_ms": t_nn,
                     "two_opt_ms": t_2opt, "nn_length_km": len_nn,
                     "two_opt_length_km": len_2opt,
                     "improvement_pct": 100 * (len_nn - len_2opt) / len_nn})
    return rows


# ------------------------------------------------------------ output
def save_csv(rows, name):
    os.makedirs(RESULTS, exist_ok=True)
    path = os.path.join(RESULTS, name)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return path


def print_table(title, rows):
    print("\n" + title)
    print("-" * len(title))
    cols = list(rows[0].keys())
    print("  ".join(f"{c:>20}" for c in cols))
    for r in rows:
        print("  ".join(f"{r[c]:>20.3f}" if isinstance(r[c], float) else f"{r[c]:>20}"
                        for c in cols))


def make_chart(rows, x_key, y_keys, labels, title, xlabel, filename):
    try:
        import matplotlib
        matplotlib.use("Agg")                  # window kholne ki zaroorat nahi
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed -> chart skipped. Run: pip install matplotlib")
        return
    plt.figure(figsize=(8, 5))
    for key, label in zip(y_keys, labels):
        plt.plot([r[x_key] for r in rows], [max(r[key], 1e-4) for r in rows],
                 marker="o", label=label)
    plt.yscale("log")
    plt.xlabel(xlabel)
    plt.ylabel("Runtime (ms, log scale)")
    plt.title(title)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    path = os.path.join(RESULTS, filename)
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"Chart saved: {path}")


def main():
    print(f"Benchmark (capacity={CAPACITY} kg, best of {REPEATS} runs per step)")

    rows_a = experiment_pipeline()
    print_table("Experiment A: pipeline runtime vs number of parcels (ms)", rows_a)
    print("CSV saved:", save_csv(rows_a, "pipeline_runtime.csv"))
    make_chart(rows_a, "parcels",
               ["sort_ms", "knapsack_ms", "dijkstra_ms", "nearest_neighbour_ms"],
               ["Merge sort", "Knapsack DP", "Dijkstra (distance table)", "Nearest neighbour"],
               "Experiment A: runtime of each step vs number of parcels",
               "Number of parcels", "pipeline_runtime.png")

    rows_b = experiment_route()
    print_table("Experiment B: route planning vs number of stops", rows_b)
    print("CSV saved:", save_csv(rows_b, "route_runtime.csv"))
    make_chart(rows_b, "stops",
               ["dijkstra_ms", "nearest_neighbour_ms", "two_opt_ms"],
               ["Dijkstra (distance table)", "Nearest neighbour", "2-opt improvement"],
               "Experiment B: route planning runtime vs number of stops",
               "Number of delivery stops", "route_runtime.png")


if __name__ == "__main__":
    main()
