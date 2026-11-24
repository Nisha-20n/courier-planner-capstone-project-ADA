"""
main.py  --  Intelligent Courier Planning System (Capstone)

Pipeline:
  1. Input padho (parcels + roads)                    -> data/input.json
  2. Parcels ko sort karo                             -> Merge Sort
  3. Van mein kya jayega?                             -> Knapsack (DP)
  4. Road network graph banao, shortest distances     -> Dijkstra
  5. Delivery route banao                             -> Nearest Neighbour + 2-opt
  6. Result print karo (har trip ke liye)

Run:  python main.py
      python main.py --show-dp                 (also prints the DP table)
      python main.py path/to/other_input.json
"""

import json
import os
import sys

from algorithms.sorting import merge_sort
from algorithms.knapsack import knapsack, print_dp_table
from algorithms.graph import Graph
from algorithms.tsp import plan_route


def load_input(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_graph(roads):
    g = Graph()
    for u, v, d in roads:
        g.add_edge(u, v, d)
    return g


def full_road_path(graph, route):
    """Expand stop-to-stop route into the actual road path via Dijkstra."""
    path = [route[0]]
    for i in range(len(route) - 1):
        segment = graph.shortest_path(route[i], route[i + 1])
        path.extend(segment[1:])
    return path


def main():
    # Default input file main.py ke folder ke andar hai, chahe kahin se bhi run karo
    default_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "input.json")
    show_dp = "--show-dp" in sys.argv
    file_args = [a for a in sys.argv[1:] if not a.startswith("--")]
    path = file_args[0] if file_args else default_path
    data = load_input(path)

    depot = data["depot"]
    capacity = data["capacity"]
    graph = build_graph(data["roads"])
    parcels = data["parcels"]

    # ---- Step 1: sab parcels ko sort karo (priority high -> low, phir value) ----
    parcels = merge_sort(parcels, key=lambda p: (p["priority"], p["value"]), reverse=True)

    print("=" * 60)
    print(" INTELLIGENT COURIER PLANNING SYSTEM")
    print("=" * 60)
    print(f"Van capacity: {capacity} kg | Depot: {depot}\n")
    print("Sorted parcels (priority high -> low):")
    print(f"  {'ID':<4} {'Wt':>3} {'Value':>6} {'Prio':>5}  Dest")
    for p in parcels:
        print(f"  {p['id']:<4} {p['weight']:>3} {p['value']:>6} {p['priority']:>5}  {p['destination']}")

    # ---- Parcels jo deliver nahi ho sakte ----
    dist_from_depot, _ = graph.dijkstra(depot)
    remaining, skipped = [], []
    for p in parcels:
        too_heavy = p["weight"] > capacity
        unreachable = dist_from_depot.get(p["destination"], float("inf")) == float("inf")
        if too_heavy or unreachable:
            skipped.append((p, "too heavy" if too_heavy else "no road to destination"))
        else:
            remaining.append(p)

    # ---- Step 2: trips banao jab tak parcels bache hain ----
    trip_no = 0
    grand_total_km = 0
    while remaining:
        trip_no += 1
        if show_dp and trip_no == 1:
            print_dp_table(remaining, capacity)      # DP table evidence (Phase 2)
        best_value, chosen = knapsack(remaining, capacity)
        if not chosen:
            break

        chosen_ids = {p["id"] for p in chosen}
        remaining = [p for p in remaining if p["id"] not in chosen_ids]

        # unique stops, order of first appearance
        stops = []
        for p in chosen:
            if p["destination"] not in stops:
                stops.append(p["destination"])

        route, total_km, nn_km = plan_route(graph, depot, stops)
        road_path = full_road_path(graph, route)
        grand_total_km += total_km
        load = sum(p["weight"] for p in chosen)

        print("\n" + "-" * 60)
        print(f" TRIP {trip_no}")
        print("-" * 60)
        print(f"Packing plan : {', '.join(p['id'] for p in chosen)}")
        print(f"Load         : {load}/{capacity} kg | Total value: {best_value}")
        print(f"Delivery order: {' -> '.join(route)}")
        print(f"Road path     : {' -> '.join(road_path)}")
        print(f"Distance      : {total_km} km (nearest-neighbour alone: {nn_km} km)")

    print("\n" + "=" * 60)
    print(f" Total trips: {trip_no} | Total distance: {grand_total_km} km")
    if skipped:
        print(" Not delivered:")
        for p, reason in skipped:
            print(f"   {p['id']} ({reason})")
    print("=" * 60)


if __name__ == "__main__":
    main()
