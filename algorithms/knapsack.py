"""
knapsack.py  --  0/1 Knapsack using Dynamic Programming (DP topic)

Problem: Van ki capacity limited hai. Har parcel ya to van mein jayega ya nahi
(0/1). Total value maximum honi chahiye aur total weight capacity se zyada nahi.
Problem: choose parcels so total value is maximum and weight <= capacity.

dp[i][c] = best value using the first i parcels with capacity c

Time complexity : O(n * capacity)
Space complexity: O(n * capacity)
Note: weights must be whole numbers (integers).
"""


def build_table(parcels, capacity):
    """Fill and return the DP table. dp[i][c] as described above."""
    n = len(parcels)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        weight = parcels[i - 1]["weight"]
        value = parcels[i - 1]["value"]
        for c in range(capacity + 1):
            dp[i][c] = dp[i - 1][c]                      # parcel skip karo
            if weight <= c:                              # parcel le lo
                take = dp[i - 1][c - weight] + value
                if take > dp[i][c]:
                    dp[i][c] = take
    return dp


def knapsack(parcels, capacity):
    """
    parcels : list of dicts with keys 'weight' (int) and 'value' (int/float)
    capacity: int
    Returns (best_value, chosen_parcels)
    """
    n = len(parcels)
    dp = build_table(parcels, capacity)

    # Backtrack: pata karo kaunse parcels chune gaye
    # Backtrack to find which parcels were chosen
    chosen = []
    c = capacity
    for i in range(n, 0, -1):
        if dp[i][c] != dp[i - 1][c]:
            chosen.append(parcels[i - 1])
            c -= parcels[i - 1]["weight"]
    chosen.reverse()

    return dp[n][capacity], chosen


def print_dp_table(parcels, capacity):
    """Print the DP table (evidence for the report). Use only for small inputs."""
    dp = build_table(parcels, capacity)
    print("\nDP table: rows = parcels considered so far, columns = capacity (kg)")
    print(f"{'':<12}" + "".join(f"{c:>5}" for c in range(capacity + 1)))
    print(f"{'(none)':<12}" + "".join(f"{v:>5}" for v in dp[0]))
    for i, p in enumerate(parcels, start=1):
        label = f"{p['id']} (w={p['weight']})"
        print(f"{label:<12}" + "".join(f"{v:>5}" for v in dp[i]))
    print(f"Best value for capacity {capacity}: {dp[len(parcels)][capacity]}")
