"""Classical Hotelling baseline: uniform customers, straight-line distance,
same price and quality, no delivery, no roads. Only locations are chosen."""
import numpy as np

np.random.seed(42)
N = 500
CX = np.random.uniform(0, 10, N)       # SIMULATED customers
CY = np.random.uniform(0, 10, N)
LOCS = [(x, y) for x in range(11) for y in range(11)]
DIST = np.array([np.hypot(CX - x, CY - y) for x, y in LOCS])   # (121, 100)
PRICE, VAR, FIXED = 150, 50, 1000

def customers(i, j):
    """Customers won by A at LOCS[i] against B at LOCS[j]; ties split."""
    return float(((DIST[i] < DIST[j]) + 0.5 * (DIST[i] == DIST[j])).sum())

def profit(n):
    return (PRICE - VAR) * n - FIXED

def best_response(player, k):
    if player == 0:
        n = [customers(i, k) for i in range(len(LOCS))]
    else:
        n = [N - customers(k, j) for j in range(len(LOCS))]
    return int(np.argmax(n))

def find_nash(i, j, max_iter=50):
    for _ in range(max_iter):
        ni = best_response(0, j)
        if customers(ni, j) <= customers(i, j): ni = i
        nj = best_response(1, ni)
        if N - customers(ni, nj) <= N - customers(ni, j): nj = j
        if (ni, nj) == (i, j):
            return i, j, True
        i, j = ni, nj
    return i, j, False

if __name__ == "__main__":
    i, j = LOCS.index((2, 5)), LOCS.index((8, 5))
    i, j, ok = find_nash(i, j)
    n = customers(i, j)
    print("Converged:", ok)
    print("A at", LOCS[i], "B at", LOCS[j])
    print("Customers: A", n, "B", N - n, "| Profit: A", profit(n), "B", profit(N - n))
    print("Customer centre (mean):", round(CX.mean(), 2), round(CY.mean(), 2))