"""Interactive UI. Run:  streamlit run src/app.py
All customer data is SIMULATED."""
import streamlit as st
import matplotlib.pyplot as plt
import game as g

st.set_page_config(page_title="Restaurant Location Game", layout="wide")
st.title("Restaurant Location Game")
st.caption("Simulated town: 100 customers, clustered demand, price/quality, "
           "delivery and asymmetric roads. Payoff = profit.")

def controls(name, default):
    st.sidebar.header(f"Restaurant {name}")
    x = st.sidebar.slider(f"{name}: x", 0, 10, default[0], key=name + "x")
    y = st.sidebar.slider(f"{name}: y", 0, 10, default[1], key=name + "y")
    p = st.sidebar.select_slider(f"{name}: price (Rs)", g.PRICES, default[2], key=name + "p")
    q = st.sidebar.select_slider(f"{name}: quality", g.QUALITIES, default[3], key=name + "q")
    r = st.sidebar.select_slider(f"{name}: delivery radius", g.RADII, default[4], key=name + "r")
    return (x, y, p, q, r)

A = controls("A", (3, 5, 150, 4, 6))
B = controls("B", (7, 5, 200, 3, 6))
res = g.evaluate(A, B)
(na, nb), (pa, pb) = res["customers"], res["profit"]

c1, c2 = st.columns([3, 2])
with c1:
    fig, ax = plt.subplots(figsize=(7, 7))
    w = res["a_wins"]
    ax.scatter(g.CX[w], g.CY[w], c="tab:blue", alpha=0.6, label="Customers -> A")
    ax.scatter(g.CX[~w], g.CY[~w], c="tab:orange", alpha=0.6, label="Customers -> B")
    for s, c, n in [(A, "tab:blue", "A"), (B, "tab:orange", "B")]:
        ax.scatter(s[0], s[1], marker="s", s=200, c=c, edgecolors="k", label=f"Restaurant {n}")
        ax.add_patch(plt.Circle((s[0], s[1]), s[4], fill=False, color=c, ls="--", alpha=0.5))
    for nm, cx, cy, _, _ in g.ANCHORS:
        ax.scatter(cx, cy, marker="*", s=250, c="k")
        ax.annotate(nm, (cx, cy), textcoords="offset points", xytext=(6, 6))
    ax.axhline(5, color="green", ls="--", alpha=0.5, label="Highway")
    ax.axvline(5.5, color="red", ls=":", alpha=0.5, label="Bridge (bottleneck)")
    ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.grid(True); ax.legend(fontsize=7)
    ax.set_title("Town map (dashed circle = delivery radius)")
    st.pyplot(fig)

with c2:
    st.subheader("Results")
    st.table({"": ["Customers", "Market share", "Profit (Rs)"],
              "A": [f"{na:.0f}", f"{na:.0f}%", f"{pa:,.0f}"],
              "B": [f"{nb:.0f}", f"{nb:.0f}%", f"{pb:,.0f}"]})
    st.subheader("Nash equilibrium check")
    if st.button("Is this a Nash equilibrium?"):
        bA, vA = g.best_response(0, B)
        bB, vB = g.best_response(1, A)
        if vA <= pa + 1e-9 and vB <= pb + 1e-9:
            st.success("Yes: neither restaurant can gain by changing its own strategy.")
        else:
            st.error("No. A profitable deviation exists:")
            if vA > pa + 1e-9: st.write(f"A could earn Rs {vA:,.0f} with {bA}")
            if vB > pb + 1e-9: st.write(f"B could earn Rs {vB:,.0f} with {bB}")
    if st.button("Find equilibrium (best-response search)"):
        a, b, ok, hist = g.find_nash(A, B)
        e = g.evaluate(a, b)
        if ok and g.is_nash(a, b):
            st.success(f"Nash equilibrium found after {len(hist)-1} moves")
        else:
            st.warning("No pure-strategy equilibrium found: best responses cycle.")
        st.write("A:", a); st.write("B:", b)
        st.write(f"Customers: A {e['customers'][0]:.0f}, B {e['customers'][1]:.0f}")
        st.write(f"Profit: A Rs {e['profit'][0]:,.0f}, B Rs {e['profit'][1]:,.0f}")
        st.caption("Strategy = (x, y, price, quality, delivery radius)")