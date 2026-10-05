"""Classical Hotelling baseline on the SAME town size (20 x 10): uniform customers,
straight-line distance, same price and quality, no delivery, no roads.
Only locations are chosen."""
import numpy as np

TOWN_W, TOWN_H = 20, 10
gx, gy = np.meshgrid(np.arange(0, TOWN_W, 1.0), np.arange(0, TOWN_H, 1.0))
rng = np.random.RandomState(42)
CX = gx.ravel() + rng.uniform(0, 1.0, gx.size)     # SIMULATED, evenly spread customers
CY = gy.ravel() + rng.uniform(0, 1.0, gy.size)
N = len(CX)
LOCS = [(x, y) for x in range(TOWN_W + 1) for y in range(TOWN_H + 1)]
DIST = np.array([np.hypot(CX - x, CY - y) for x, y in LOCS])
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
    i, j = LOCS.index((4, 5)), LOCS.index((16, 5))
    i, j, ok = find_nash(i, j)
    n = customers(i, j)
    print("Converged:", ok)
    print("A at", LOCS[i], "B at", LOCS[j])
    print("Customers: A", n, "B", N - n, "| Profit: A", profit(n), "B", profit(N - n))
    print("Customer centre (mean):", round(CX.mean(), 2), round(CY.mean(), 2))