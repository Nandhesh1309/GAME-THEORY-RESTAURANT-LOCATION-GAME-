"""Static demo plot of one scenario (uses the same engine as the app)."""
import matplotlib.pyplot as plt
import game as g

A = (6.0, 5.0, 150, 4, 6)
B = (14.0, 5.0, 175, 4, 6)
res = g.evaluate(A, B)
na, nb = res["customers"]; pa, pb = res["profit"]
w = res["a_wins"]

fig, ax = plt.subplots(figsize=(12, 6.5))
ax.add_patch(plt.Rectangle((0, 0), g.TOWN_W, g.TOWN_H, fill=False, lw=2, ec="gray"))
for i, (rid, (nm, bx)) in enumerate(g.BRIDGES.items()):
    ax.axvspan(bx + 0.2, bx + 0.8, color="red", alpha=.15, label="Bridge (bottleneck)" if i == 0 else None)
    ax.annotate(nm, (bx + 0.5, 0.3), ha="center", fontsize=8, color="darkred")
ax.scatter(g.CX[w], g.CY[w], s=8, c="tab:blue", alpha=.6)
ax.scatter(g.CX[~w], g.CY[~w], s=8, c="tab:orange", alpha=.6)
ax.scatter(*A[:2], s=300, c="tab:blue", edgecolors="k", label=f"A: {na:.0f} customers, profit {pa:,.0f}")
ax.scatter(*B[:2], s=300, c="tab:orange", edgecolors="k", label=f"B: {nb:.0f} customers, profit {pb:,.0f}")
for nm, cx, cy, _, _ in g.ANCHORS:
    ax.scatter(cx, cy, marker="D", s=60, c="gold", edgecolors="k")
    ax.annotate(nm, (cx, cy), textcoords="offset points", xytext=(0, 10), ha="center", fontsize=9)
for nm, cx, cy, _, _ in g.RESIDENTIAL:
    ax.scatter(cx, cy, marker="s", s=50, c="limegreen", edgecolors="k")
    ax.annotate(nm, (cx, cy), textcoords="offset points", xytext=(0, -14), ha="center", fontsize=7)
ax.set_xlim(-.5, g.TOWN_W + .5); ax.set_ylim(-.5, g.TOWN_H + .5)
ax.set_title("Restaurant Location Game - TOWN"); ax.legend(loc="upper right", fontsize=8)
plt.show()