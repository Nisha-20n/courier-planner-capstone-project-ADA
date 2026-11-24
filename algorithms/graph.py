"""
graph.py  --  Weighted graph + Dijkstra (Graph Algorithms topic)

Nodes  = locations (Depot, A, B, ...)
Edges  = roads with distance in km (undirected)

Dijkstra finds the shortest distance from one location to all others.

Time complexity : O((V + E) log V) using a min-heap
Space complexity: O(V + E)
"""

import heapq


class Graph:
    def __init__(self):
        self.adj = {}   # {node: [(neighbour, distance), ...]}

    def add_edge(self, u, v, dist):
        self.adj.setdefault(u, []).append((v, dist))
        self.adj.setdefault(v, []).append((u, dist))   # road dono taraf jaati hai

    def dijkstra(self, source):
        """Return (dist, prev). dist[node] = shortest km from source."""
        dist = {node: float("inf") for node in self.adj}
        prev = {node: None for node in self.adj}
        dist[source] = 0
        heap = [(0, source)]

        while heap:
            d, u = heapq.heappop(heap)
            if d > dist[u]:
                continue                       # purani (stale) entry
            for v, w in self.adj[u]:
                nd = d + w
                if nd < dist[v]:
                    dist[v] = nd
                    prev[v] = u
                    heapq.heappush(heap, (nd, v))
        return dist, prev

    def shortest_path(self, source, target):
        """Return the list of nodes on the shortest road path source -> target."""
        _, prev = self.dijkstra(source)
        path = []
        node = target
        while node is not None:
            path.append(node)
            node = prev[node]
        path.reverse()
        return path if path and path[0] == source else []
