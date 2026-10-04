"""Game engine: customers, roads, profit, best response, Nash equilibrium.
All customer data is SIMULATED."""
import numpy as np
import networkx as nx

TOWN_SIZE = 10
N_CUSTOMERS = 100
VAR_COST, FIXED_COST = 50, 1000
PRICES, QUALITIES, RADII = [100, 150, 200, 250], [1, 2, 3, 4, 5], [2, 4, 6, 8]
LOCS = range(TOWN_SIZE + 1)
STRATEGIES = [(x, y, p, q, r) for x in LOCS for y in LOCS
              for p in PRICES for q in QUALITIES for r in RADII]   # 9680

ANCHORS = [("Town centre", 5.0, 5.0, 1.0, 40),
           ("Shopping mall", 2.0, 8.0, 0.8, 20),
           ("Business district", 8.0, 2.5, 0.8, 20)]

def make_customers(seed=42):
    rng = np.random.RandomState(seed)
    xs, ys = [], []
    for _, cx, cy, s, n in ANCHORS:
        xs.append(rng.normal(cx, s, n)); ys.append(rng.normal(cy, s, n))
    rest = N_CUSTOMERS - sum(a[4] for a in ANCHORS)
    xs.append(rng.uniform(0, TOWN_SIZE, rest)); ys.append(rng.uniform(0, TOWN_SIZE, rest))
    return (np.clip(np.concatenate(xs), 0, TOWN_SIZE),
            np.clip(np.concatenate(ys), 0, TOWN_SIZE))

CX, CY = make_customers()

FAST, NORMAL, SLOW, BOTTLENECK = 0.7, 1.0, 1.5, 2.0

def build_road_network(size=TOWN_SIZE):
    G = nx.DiGraph()
    for x in range(size + 1):
        for y in range(size + 1):
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                x2, y2 = x + dx, y + dy
                if not (0 <= x2 <= size and 0 <= y2 <= size):
                    continue
                w = NORMAL
                if dy == 0 and y == 5: w = FAST
                elif x <= 3 and y >= 7 and x2 <= 3: w = SLOW
                elif x == 5 and x2 == 6: w = BOTTLENECK
                elif x == 6 and x2 == 5: w = SLOW
                G.add_edge((x, y), (x2, y2), weight=w)
    return G

ROADS_REV = build_road_network().reverse()
_GX = np.clip(np.rint(CX), 0, TOWN_SIZE).astype(int)
_GY = np.clip(np.rint(CY), 0, TOWN_SIZE).astype(int)
_SNAP = np.hypot(CX - _GX, CY - _GY)
_cache = {}

def travel_cost(x, y):
    """Road travel cost from every customer to a restaurant at (x, y)."""
    if (x, y) not in _cache:
        d = nx.single_source_dijkstra_path_length(ROADS_REV, (x, y), weight="weight")
        _cache[(x, y)] = np.array([d[(a, b)] for a, b in zip(_GX, _GY)]) + _SNAP
    return _cache[(x, y)]

def customer_cost(s):
    """Lowest cost for each customer (dine-in or delivery)."""
    x, y, p, q, r = s
    dine = p + 10 * travel_cost(x, y) - 5 * q
    dist = np.hypot(CX - x, CY - y)
    deliv = p + (10 + 2 * dist) - 5 * q
    return np.where(dist <= r, np.minimum(dine, deliv), dine)

def profit(s, n):
    return (s[2] - VAR_COST) * n - FIXED_COST

# Cost of every customer for every strategy (computed once): shape (9680, 100)
COSTS = np.array([customer_cost(s) for s in STRATEGIES])
PRICE_ARR = np.array([s[2] for s in STRATEGIES])
INDEX = {s: i for i, s in enumerate(STRATEGIES)}

def _share(ca, cb):
    """Customers won by A. Ties are split 50/50 (fair)."""
    return (ca < cb) + 0.5 * (ca == cb)

def evaluate(sa, sb):
    """Returns customers, market share (%) and profit for A and B."""
    w = _share(COSTS[INDEX[sa]], COSTS[INDEX[sb]])
    na = float(w.sum()); nb = N_CUSTOMERS - na
    return {"customers": (na, nb), "share": (na, nb),
            "profit": (profit(sa, na), profit(sb, nb)), "a_wins": w > 0.5}

def best_response(player, other):
    """Best strategy for `player` (0=A, 1=B) given the other's strategy."""
    oc = COSTS[INDEX[other]]
    if player == 0:
        n = _share(COSTS, oc).sum(axis=1)
    else:
        n = N_CUSTOMERS - _share(oc, COSTS).sum(axis=1)
    pr = (PRICE_ARR - VAR_COST) * n - FIXED_COST
    i = int(np.argmax(pr))
    return STRATEGIES[i], float(pr[i])

def find_nash(sa, sb, max_iter=50):
    """Best-response iteration. Returns (sa, sb, converged, history)."""
    hist = [(sa, sb)]
    for _ in range(max_iter):
        cur = evaluate(sa, sb)["profit"][0]
        new_a, pa = best_response(0, sb)
        if pa <= cur + 1e-9: new_a = sa
        cur = evaluate(new_a, sb)["profit"][1]
        new_b, pb = best_response(1, new_a)
        if pb <= cur + 1e-9: new_b = sb
        if new_a == sa and new_b == sb:
            return sa, sb, True, hist
        sa, sb = new_a, new_b
        if (sa, sb) in hist:                       # cycle detected
            hist.append((sa, sb))
            return sa, sb, False, hist
        hist.append((sa, sb))
    return sa, sb, False, hist

def is_nash(sa, sb):
    """Verify no profitable unilateral deviation."""
    cur = evaluate(sa, sb)["profit"]
    return (best_response(0, sb)[1] <= cur[0] + 1e-9 and
            best_response(1, sa)[1] <= cur[1] + 1e-9)

if __name__ == "__main__":
    A, B = (3, 5, 150, 4, 6), (7, 5, 200, 3, 6)
    print("Start:", evaluate(A, B)["customers"], evaluate(A, B)["profit"])
    a, b, ok, h = find_nash(A, B)
    e = evaluate(a, b)
    print("Converged:", ok, "after", len(h) - 1, "moves")
    print("A:", a, "B:", b)
    print("Customers:", e["customers"], "Profit:", e["profit"])
    print("Verified Nash:", is_nash(a, b))