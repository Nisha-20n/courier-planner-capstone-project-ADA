"""
tsp.py  --  Route planning with Approximation (Approximation topic)

Best delivery order = Travelling Salesman Problem (TSP). TSP is NP-hard, so
checking every order is far too slow for many stops (n! orders).
Isliye hum "almost best" answer nikalte hain:

  1. Nearest Neighbour : hamesha sabse paas wale unvisited stop pe jao.
                         Time O(n^2). Fast but not always optimal.
  2. 2-opt improvement : route ke do hisse ulte karke dekho, agar chhota ho
                         jaye to rakh lo. As written, each pass is O(k^3)
                         (O(k^2) pairs, and each pair recomputes the route
                         length in O(k)). Can be made O(k^2) per pass by
                         computing only the change in length (see report).

Distances between stops come from Dijkstra (graph.py).
"""


def build_distance_table(graph, nodes):
    """dist_table[a][b] = shortest road distance between a and b."""
    table = {}
    for a in nodes:
        dist, _ = graph.dijkstra(a)
        table[a] = {b: dist[b] for b in nodes}
    return table


def route_length(route, table):
    return sum(table[route[i]][route[i + 1]] for i in range(len(route) - 1))


def nearest_neighbour(depot, stops, table):
    """Return a round-trip route: depot -> ... -> depot."""
    route = [depot]
    unvisited = list(stops)          # list (not set) => same answer on every run when distances tie
    current = depot
    while unvisited:
        nxt = min(unvisited, key=lambda s: table[current][s])
        route.append(nxt)
        unvisited.remove(nxt)
        current = nxt
    route.append(depot)
    return route


def two_opt(route, table):
    """Improve a route by reversing segments while it gets shorter."""
    best = route[:]
    improved = True
    while improved:
        improved = False
        for i in range(1, len(best) - 2):
            for j in range(i + 1, len(best) - 1):
                candidate = best[:i] + best[i:j + 1][::-1] + best[j + 1:]
                if route_length(candidate, table) < route_length(best, table):
                    best = candidate
                    improved = True
    return best


def plan_route(graph, depot, stops):
    """
    Returns (route, total_km, nn_km)
      route    : ordered list of stops, starts and ends at depot
      total_km : length after 2-opt improvement
      nn_km    : length of the plain nearest-neighbour route (for comparison)
    """
    nodes = [depot] + list(stops)
    table = build_distance_table(graph, nodes)
    nn_route = nearest_neighbour(depot, stops, table)
    best = two_opt(nn_route, table)
    return best, route_length(best, table), route_length(nn_route, table)
