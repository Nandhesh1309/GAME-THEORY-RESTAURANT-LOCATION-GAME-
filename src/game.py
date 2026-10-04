"""Game engine: customers, roads, profit, best response, Nash equilibrium.
All customer data is SIMULATED.

Town = 20 wide x 10 high. Restaurants can be placed ANYWHERE (continuous x, y).
The equilibrium search looks for deviations on a whole-number location grid
(plus price / quality / delivery choices)."""
import numpy as np
import networkx as nx

TOWN_W, TOWN_H = 20, 10
TOWN_SIZE = TOWN_H                      # kept for backward compatibility
VAR_COST, FIXED_COST = 50, 1000
PRICES = [100, 125, 150, 175, 200, 225, 250]
QUALITIES = [1, 2, 3, 4, 5]
RADII = [2, 4, 6, 8]
LOCS_X = range(TOWN_W + 1)
LOCS_Y = range(TOWN_H + 1)
LOCS = LOCS_X
STRATEGIES = [(x, y, p, q, r) for x in LOCS_X for y in LOCS_Y
              for p in PRICES for q in QUALITIES for r in RADII]

# Demand hubs: (name, centre_x, centre_y, spread, customers)
ANCHORS = [("Town centre",      8.0, 5.0, 1.4, 200),
           ("Shopping mall",    3.0, 8.0, 1.0, 110),
           ("Business district", 16.0, 2.5, 1.2, 130)]

def make_customers(seed=42):
    """Hub customers (dense areas) + evenly spread customers over the WHOLE town
    (one per 0.5 x 0.5 cell, jittered) so empty areas also have people."""
    rng = np.random.RandomState(seed)
    xs, ys = [], []
    for _, cx, cy, s, n in ANCHORS:
        xs.append(rng.normal(cx, s, n)); ys.append(rng.normal(cy, s, n))
    gx, gy = np.meshgrid(np.arange(0, TOWN_W, 0.5), np.arange(0, TOWN_H, 0.5))
    xs.append(gx.ravel() + rng.uniform(0, 0.5, gx.size))
    ys.append(gy.ravel() + rng.uniform(0, 0.5, gy.size))
    return (np.clip(np.concatenate(xs), 0, TOWN_W),
            np.clip(np.concatenate(ys), 0, TOWN_H))

CX, CY = make_customers()
N_CUSTOMERS = len(CX)

# Road speeds (lower = faster)
FAST, NORMAL, BOTTLENECK, SLOW_BACK = 0.7, 1.0, 2.0, 1.5
BRIDGE_X = 10          # bridge between x=10 and x=11
HIGHWAY_Y = 5          # highway runs along y = 5

def build_road_network():
    G = nx.DiGraph()
    for x in range(TOWN_W + 1):
        for y in range(TOWN_H + 1):
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                x2, y2 = x + dx, y + dy
                if not (0 <= x2 <= TOWN_W and 0 <= y2 <= TOWN_H):
                    continue
                w = NORMAL
                if dy == 0 and y == HIGHWAY_Y: w = FAST                          # highway
                elif x == BRIDGE_X and x2 == BRIDGE_X + 1: w = BOTTLENECK  # bridge, eastbound
                elif x == BRIDGE_X + 1 and x2 == BRIDGE_X: w = SLOW_BACK   # bridge, westbound
                G.add_edge((x, y), (x2, y2), weight=w)
    return G

ROADS_REV = build_road_network().reverse()
_GX = np.clip(np.rint(CX), 0, TOWN_W).astype(int)
_GY = np.clip(np.rint(CY), 0, TOWN_H).astype(int)
_SNAP = np.hypot(CX - _GX, CY - _GY)
_node_cache = {}

def travel_cost(x, y):
    """Road travel cost from every customer to a restaurant at ANY point (x, y)."""
    nx_ = int(np.clip(round(x), 0, TOWN_W)); ny_ = int(np.clip(round(y), 0, TOWN_H))
    if (nx_, ny_) not in _node_cache:
        d = nx.single_source_dijkstra_path_length(ROADS_REV, (nx_, ny_), weight="weight")
        _node_cache[(nx_, ny_)] = np.array([d[(a, b)] for a, b in zip(_GX, _GY)]) + _SNAP
    return _node_cache[(nx_, ny_)] + np.hypot(x - nx_, y - ny_)

def customer_cost(s):
    """Lowest cost for each customer (dine-in or delivery)."""
    x, y, p, q, r = s
    dine = p + 12 * travel_cost(x, y) - 4 * q
    dist = np.hypot(CX - x, CY - y)
    deliv = p + (30 + 5 * dist) - 4 * q
    return np.where(dist <= r, np.minimum(dine, deliv), dine).astype(np.float32)

def profit(s, n):
    return (s[2] - VAR_COST) * n - FIXED_COST

# Cost of every customer for every grid strategy (computed once)
COSTS = np.array([customer_cost(s) for s in STRATEGIES], dtype=np.float32)
PRICE_ARR = np.array([s[2] for s in STRATEGIES])
INDEX = {s: i for i, s in enumerate(STRATEGIES)}
_free_cache = {}

def cost_of(s):
    """Customer costs for any strategy (grid or freely placed)."""
    s = tuple(s)
    if s in INDEX:
        return COSTS[INDEX[s]]
    if s not in _free_cache:
        if len(_free_cache) > 500: _free_cache.clear()
        _free_cache[s] = customer_cost(s)
    return _free_cache[s]

def _share(ca, cb):
    """Customers won by A. Ties are split 50/50 (fair)."""
    return (ca < cb) + 0.5 * (ca == cb)

def evaluate(sa, sb):
    """Returns customers, market share and profit for A and B."""
    w = _share(cost_of(sa), cost_of(sb))
    na = float(w.sum()); nb = N_CUSTOMERS - na
    return {"customers": (na, nb), "share": (na, nb),
            "profit": (profit(sa, na), profit(sb, nb)), "a_wins": w > 0.5, "w": w}

def best_response(player, other):
    """Best strategy (searched on the grid) for `player` (0=A, 1=B) given the other's."""
    oc = cost_of(other)
    if player == 0:
        n = _share(COSTS, oc).sum(axis=1)
    else:
        n = N_CUSTOMERS - _share(oc, COSTS).sum(axis=1)
    pr = (PRICE_ARR - VAR_COST) * n - FIXED_COST
    i = int(np.argmax(pr))
    return STRATEGIES[i], float(pr[i])

def find_nash(sa, sb, max_iter=50):
    """Best-response iteration. Returns (sa, sb, converged, history)."""
    sa, sb = tuple(sa), tuple(sb)
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
    A, B = (6, 5, 150, 4, 6), (14, 5, 175, 4, 6)
    print("Customers in town:", N_CUSTOMERS)
    print("Start:", evaluate(A, B)["customers"], evaluate(A, B)["profit"])
    a, b, ok, h = find_nash(A, B)
    e = evaluate(a, b)
    print("Converged:", ok, "after", len(h) - 1, "moves")
    print("A:", a, "B:", b)
    print("Customers:", e["customers"], "Profit:", e["profit"])
    print("Verified Nash:", is_nash(a, b))