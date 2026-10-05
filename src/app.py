import streamlit as st
import plotly.graph_objects as go
import numpy as np
import os, importlib.util

# Load game.py from the SAME folder as this app.py (avoids stale or wrong copies of game.py)
_GAME_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "game.py")

@st.cache_resource(show_spinner="Loading game engine (first start takes a few seconds)...")
def _load_engine(path, mtime):
    spec = importlib.util.spec_from_file_location("game_engine", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

g = _load_engine(_GAME_PATH, os.path.getmtime(_GAME_PATH))
if not hasattr(g, "TOWN_W"):
    st.error(f"The game.py at:\n\n{_GAME_PATH}\n\nis an OLD version (no TOWN_W). "
             "Replace it with the new game.py from the zip, then restart Streamlit.")
    st.stop()
N = g.N_CUSTOMERS

st.set_page_config(page_title="Spatial Market | Restaurant Game", page_icon="🍽️", layout="wide", initial_sidebar_state="collapsed")

# ---------- Theme ----------
st.markdown("""
<style>
:root { color-scheme: dark; }
.stApp { background: #070b12; }
[data-testid="stHeader"] { background: rgba(0,0,0,0); }
[data-testid="stSidebar"] { display:none; }
.block-container { max-width: 100% !important; padding: 1.0rem 1.4rem 0.5rem !important; }
.hero { display:flex; justify-content:space-between; align-items:center; margin-bottom: .55rem; }
.brand { font-size: 1.35rem; font-weight: 800; letter-spacing: .02em; }
.brand span { color:#8ea2ff; }
.pill { border:1px solid #273247; background:#0d1421; padding:.38rem .65rem; border-radius:999px; color:#aab7ca; font-size:.78rem; }
.card { background:linear-gradient(180deg,#101826,#0b111c); border:1px solid #202b3d; border-radius:18px; padding:14px 16px; }
.card-title { color:#94a3b8; font-size:.72rem; text-transform:uppercase; letter-spacing:.14em; }
.big { font-size:1.55rem; font-weight:800; }
.a { color:#5fa8ff; } .b { color:#ff9d4d; }
[data-testid="stMetric"] { background:#0e1623; border:1px solid #202b3d; border-radius:16px; padding:10px 12px; }
[data-testid="stExpander"] { border:1px solid #273247 !important; border-radius:18px !important; background:#0c131f !important; }
[data-testid="stExpander"] summary p { font-weight:800; letter-spacing:.08em; }
div[data-testid="stHorizontalBlock"] { gap: .7rem; }
button[kind="secondary"] { border-radius:12px; }
@keyframes slideUp { from {transform:translateY(60px);opacity:0} to {transform:translateY(0);opacity:1} }
div[data-testid="stDialog"] div[role="dialog"] { animation: slideUp .4s cubic-bezier(.2,.8,.2,1); border-radius:20px; }
</style>
""", unsafe_allow_html=True)

import inspect as _inspect
def _stretch_kw(fn):
    params = _inspect.signature(fn).parameters
    if "width" in params:
        return {"width": "stretch"}
    return {"use_container_width": True} if "use_container_width" in params else {}

W, H = g.TOWN_W, g.TOWN_H

# ---------- State ----------
if "placing" not in st.session_state:
    st.session_state.placing = "A"
if "A" not in st.session_state:
    st.session_state.A = [6.0, 5.0, 150, 4, 6]
if "B" not in st.session_state:
    st.session_state.B = [14.0, 5.0, 175, 4, 6]

if "closed" not in st.session_state:
    st.session_state.closed = set()
if g.CLOSED != frozenset(st.session_state.closed):
    with st.spinner("Updating roads (about 2 seconds)..."):
        g.set_closed(st.session_state.closed)

def _sync_widgets():
    for n in ("A", "B"):
        s_ = st.session_state[n]
        st.session_state[f"price_{n}"] = s_[2]
        st.session_state[f"quality_{n}"] = s_[3]
        st.session_state[f"radius_{n}"] = s_[4]

if st.session_state.pop("_needs_sync", False) or "price_A" not in st.session_state:
    _sync_widgets()

def _snap(v, options):
    return min(options, key=lambda o: abs(o - v))

def _valid(s):
    return [round(float(min(max(s[0], 0), W)), 2), round(float(min(max(s[1], 0), H)), 2),
            _snap(s[2], g.PRICES), _snap(s[3], g.QUALITIES), _snap(s[4], g.RADII)]

st.session_state.A = _valid(st.session_state.A)
st.session_state.B = _valid(st.session_state.B)
A = tuple(st.session_state.A); B = tuple(st.session_state.B)
res = g.evaluate(A, B)
na, nb = res["customers"]; pa, pb = res["profit"]

# ---------- Header ----------
st.markdown('<div class="hero"><div class="brand">SPATIAL <span>MARKET</span> · RESTAURANT GAME</div><div class="pill">SIMULATED TOWN · STRATEGIC MODE</div></div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns([1, 1, 1.3])
cards = {}
with c1: cards["A"] = st.empty()
with c2: cards["B"] = st.empty()
with c3:
    if st.session_state.get("placing") not in ("A", "B"):
        st.session_state.placing = "A"
    st.segmented_control("Place restaurant", ["A", "B"], key="placing",
                         format_func=lambda v: f"Place {v}",
                         help="Choose a restaurant, then click anywhere inside the town to put it there.")

left, right = st.columns(2)
for col, name in [(left, "A"), (right, "B")]:
    with col:
        s = st.session_state[name]
        st.markdown(f'<div class="card"><div class="card-title">{name} · strategy</div>', unsafe_allow_html=True)
        q1, q2, q3 = st.columns(3)
        with q1: s[2] = st.select_slider("Price", g.PRICES, key=f"price_{name}")
        with q2: s[3] = st.select_slider("Quality", g.QUALITIES, key=f"quality_{name}")
        with q3: s[4] = st.select_slider("Delivery", g.RADII, key=f"radius_{name}", format_func=lambda x: f"{x} km")
        st.session_state[name] = s
        st.markdown('</div>', unsafe_allow_html=True)

# ---------- Road controls (switch off = road closed) ----------
_ver = st.session_state.get("_road_ver", 0)
st.markdown('<div class="card-title" style="margin:.7rem 0 .25rem">Bridges · switch OFF to close a bridge</div>',
            unsafe_allow_html=True)
_rc = st.columns(len(g.ALL_ROADS))
_new_closed = set()
for _col, _rid in zip(_rc, g.ALL_ROADS):
    _nm = g.BRIDGES[_rid][0]
    if not _col.toggle(f"🌉 {_nm}", value=_rid not in st.session_state.closed, key=f"road_{_rid}_{_ver}"):
        _new_closed.add(_rid)
st.session_state.closed = _new_closed
if g.CLOSED != frozenset(_new_closed):
    with st.spinner("Updating bridges..."):
        g.set_closed(_new_closed)
CLOSED = set(_new_closed)

A = tuple(st.session_state.A); B = tuple(st.session_state.B)
res = g.evaluate(A, B)
na, nb = res["customers"]; pa, pb = res["profit"]
cards["A"].markdown(f'<div class="card"><div class="card-title">Restaurant A · {na:.0f} customers</div><div class="big a">₹{pa:,.0f}</div><div style="color:#7f8ea3">Profit · {na/N*100:.0f}% market share</div></div>', unsafe_allow_html=True)
cards["B"].markdown(f'<div class="card"><div class="card-title">Restaurant B · {nb:.0f} customers</div><div class="big b">₹{pb:,.0f}</div><div style="color:#7f8ea3">Profit · {nb/N*100:.0f}% market share</div></div>', unsafe_allow_html=True)

# ---------- Info popup ----------
def _info_body():
    A_, B_ = tuple(st.session_state.A), tuple(st.session_state.B)
    r = g.evaluate(A_, B_); na_, nb_ = r["customers"]; pa_, pb_ = r["profit"]
    m1, m2, m3 = st.columns(3)
    m1.metric("Customers", f"{na_:.0f} / {nb_:.0f}", "A / B")
    m2.metric("Market share", f"{na_/N*100:.0f}% / {nb_/N*100:.0f}%", "A / B")
    m3.metric("Profit", f"₹{pa_:,.0f} / ₹{pb_:,.0f}", "A / B")
    st.markdown("**How customers choose** · each customer compares price, quality, road travel cost "
                "and delivery, and picks the cheapest overall option.")
    with st.spinner("Checking for profitable deviations..."):
        _, vA = g.best_response(0, B_); _, vB = g.best_response(1, A_)
    if vA <= pa_ + 1e-9 and vB <= pb_ + 1e-9:
        st.success("✅ Nash equilibrium: neither restaurant can gain by changing its own strategy.")
    else:
        st.warning("⚠️ Not a Nash equilibrium: at least one restaurant can earn more by changing strategy.")
        st.write(f"A's best-response profit: ₹{vA:,.0f}  ·  B's best-response profit: ₹{vB:,.0f}")
    if "eq_result" in st.session_state:
        a, b, ok, e, moves, was_nash = st.session_state.eq_result
        st.markdown("---")
        st.markdown("**Last equilibrium search**")
        st.write(("Your starting positions were already a Nash equilibrium. " if was_nash else
                  "Your starting positions were NOT a Nash equilibrium. ")
                 + ("Search converged" if ok else "Search entered a cycle (no pure equilibrium found)")
                 + f" after {moves} moves.")
        st.write(f"🔵 A → price ₹{a[2]}, quality {a[3]}, delivery {a[4]} km · serves {e['customers'][0]:.0f}")
        st.write(f"🟠 B → price ₹{b[2]}, quality {b[3]}, delivery {b[4]} km · serves {e['customers'][1]:.0f}")
        if a[:2] == b[:2]:
            st.info("Both restaurants chose the same spot (they appear side by side on the map).")

_dlg = getattr(st, "dialog", None) or getattr(st, "experimental_dialog", None)
if _dlg:
    show_info = _dlg("Game intelligence")(_info_body)
else:
    def show_info():
        with st.expander("Game intelligence", expanded=True):
            _info_body()

bc1, bc2, _sp = st.columns([1, 1.3, 4])
if bc1.button("ℹ️ Game info", **_stretch_kw(st.button)):
    show_info()
if bc2.button("🔍 Check equilibrium", type="primary", **_stretch_kw(st.button)):
    with st.spinner("Searching for equilibrium (up to ~20 seconds)..."):
        was_nash = g.is_nash(A, B)
        a, b, ok, h = g.find_nash(A, B)
        e = g.evaluate(a, b)
    st.session_state.A = list(a); st.session_state.B = list(b)
    st.session_state._needs_sync = True
    st.session_state._map_n = st.session_state.get("_map_n", 0) + 1
    st.session_state.eq_result = (a, b, ok, e, len(h) - 1, was_nash)
    st.session_state._open_info = True
    st.rerun()

# ---------- Click layer (free placement, 0.25 resolution) ----------
def zone_text(x, y, closed=()):
    z = []
    for rid, (nm, bx) in g.BRIDGES.items():
        if bx <= x <= bx + 1:
            z.append(f"⛔ {nm} · CLOSED" if rid in closed else f"🌉 {nm} · bottleneck")
    for nm, cx, cy, sp, _n in g.ANCHORS:
        if np.hypot(x - cx, y - cy) <= sp * 1.6:
            z.append({"Town centre": "🏙️ Town centre · dense demand",
                      "Shopping mall": "🛍️ Shopping mall · demand hub",
                      "Business district": "🏢 Business district · demand hub"}[nm])
    for nm, cx, cy, sp, _n in g.RESIDENTIAL:
        if np.hypot(x - cx, y - cy) <= sp * 1.6:
            z.append(f"🏠 {nm} · residential area")
    return "<br>".join(z) if z else "Free area · open land"

@st.cache_data
def click_layer(closed=()):
    xs = np.arange(0, W + 1e-9, 0.25); ys = np.arange(0, H + 1e-9, 0.25)
    gx, gy, gd = [], [], []
    for x in xs:
        for y in ys:
            gx.append(float(x)); gy.append(float(y)); gd.append(["grid", float(x), float(y), zone_text(x, y, closed)])
    return gx, gy, gd

# ---------- Map ----------
fig = go.Figure()
PAD = 0.5

fig.add_shape(type="rect", x0=0, x1=W, y0=0, y1=H, fillcolor="#0c1420",
              line=dict(color="rgba(150,170,215,.75)", width=2.5), layer="below")
fig.add_annotation(x=0.2, y=H-0.15, text="<b>TOWN</b>", showarrow=False, xanchor="left", yanchor="top",
                   font=dict(size=13, color="rgba(170,185,215,.75)"))

# Hub markings (gold diamond + framed label)
hub_icon = {"Town centre": "🏙️", "Shopping mall": "🛍️", "Business district": "🏢"}
fig.add_trace(go.Scatter(x=[h[1] for h in g.ANCHORS], y=[h[2] for h in g.ANCHORS], mode="markers",
                         marker=dict(symbol="diamond", size=13, color="rgba(255,214,102,.95)",
                                     line=dict(color="#fff3c4", width=1.5)),
                         hoverinfo="skip", showlegend=False))
for nm, cx, cy, sp, _n in g.ANCHORS:
    fig.add_annotation(x=cx, y=cy, yshift=24, text=f"{hub_icon[nm]} <b>{nm}</b>", showarrow=False,
                       font=dict(size=11, color="#ffe9a8"), bgcolor="rgba(40,32,8,.85)",
                       bordercolor="rgba(255,214,102,.7)", borderwidth=1, borderpad=3)

# Residential area markings (green square + framed label)
fig.add_trace(go.Scatter(x=[r[1] for r in g.RESIDENTIAL], y=[r[2] for r in g.RESIDENTIAL], mode="markers",
                         marker=dict(symbol="square", size=11, color="rgba(110,220,150,.95)",
                                     line=dict(color="#d9ffe8", width=1.5)),
                         hoverinfo="skip", showlegend=False))
for nm, cx, cy, sp, _n in g.RESIDENTIAL:
    fig.add_annotation(x=cx, y=cy, yshift=-22, text=f"🏠 {nm}", showarrow=False,
                       font=dict(size=10, color="#c9f5d9"), bgcolor="rgba(8,34,20,.85)",
                       bordercolor="rgba(110,220,150,.6)", borderwidth=1, borderpad=3)

# Bridges (red = open bottleneck, dark = closed)
for k, (rid, (nm, bx)) in enumerate(g.BRIDGES.items()):
    closed_ = rid in CLOSED
    fig.add_shape(type="rect", x0=bx+0.2, x1=bx+0.8, y0=0, y1=H,
                  fillcolor="rgba(20,20,26,.9)" if closed_ else "rgba(255,110,110,.09)",
                  line=dict(color="rgba(255,70,70,.95)" if closed_ else "rgba(255,120,120,.55)",
                            width=2 if closed_ else 1.2, dash="solid" if closed_ else "dash"), layer="below")
    fig.add_annotation(x=bx+0.5, y=0.45 if k % 2 == 0 else H-0.45,
                       text=(f"⛔ {nm}<br>CLOSED" if closed_ else f"🌉 {nm}<br>(slow)"), showarrow=False,
                       font=dict(size=10, color="rgba(255,90,90,1)" if closed_ else "rgba(255,140,140,.95)"),
                       bgcolor="rgba(12,20,32,.9)")

# Customers: blue -> A, orange -> B, violet -> tie
w = res["w"]
for mask, col in ((w == 1, "#5fa8ff"), (w == 0, "#ff9d4d"), (w == 0.5, "#c4a8ff")):
    if mask.any():
        fig.add_trace(go.Scattergl(x=g.CX[mask], y=g.CY[mask], mode="markers",
                                   marker=dict(size=5, color=col, opacity=.7), hoverinfo="skip", showlegend=False))

# Restaurants (side by side if they share a spot)
same = (abs(A[0]-B[0]) < 0.6 and abs(A[1]-B[1]) < 0.6)
off = 0.3 if same else 0.0
for s_, nm, col, edge, dx in ((A, "A", "#5fa8ff", "#dbeafe", -off), (B, "B", "#ff9d4d", "#ffedd5", off)):
    fig.add_trace(go.Scatter(x=[s_[0]+dx], y=[s_[1]], mode="markers+text", text=[nm], textposition="middle center",
                             marker=dict(size=30, color=col, line=dict(color=edge, width=2)),
                             textfont=dict(color="#07101c", size=14), hoverinfo="skip", showlegend=False))

gx, gy, gd = click_layer(tuple(sorted(CLOSED)))
fig.add_trace(go.Scatter(x=gx, y=gy, mode="markers", marker=dict(size=14, color="rgba(255,255,255,0.01)"),
                         customdata=gd, hovertemplate="%{customdata[3]}<extra></extra>",
                         hoverlabel=dict(bgcolor="#101826", font=dict(color="#e2e8f0", size=12)), showlegend=False))

fig.update_layout(
    height=640, margin=dict(l=0, r=0, t=0, b=0),
    paper_bgcolor="#070b12", plot_bgcolor="#070b12",
    xaxis=dict(range=[-PAD, W+PAD], visible=False, fixedrange=True),
    yaxis=dict(range=[-PAD, H+PAD], visible=False, fixedrange=True),
    showlegend=False, clickmode="event+select", dragmode=False,
    hovermode="closest", hoverdistance=-1,
)

st.markdown('<div style="margin:.5rem 0 .3rem;color:#718096;font-size:.76rem;letter-spacing:.13em;text-transform:uppercase">'
            'Choose A or B at the top, then click anywhere inside the town to place it · hover to see what is there</div>',
            unsafe_allow_html=True)
st.markdown('<div style="font-size:.8rem;color:#aab7ca;margin-bottom:.4rem">'
            '🌉 Bridge (slow) &nbsp;·&nbsp; ⛔ Closed bridge &nbsp;·&nbsp; '
            '<span style="color:#ffd666">◆</span> 🏙️🛍️🏢 Demand hubs &nbsp;·&nbsp; '
            '<span style="color:#6edc96">■</span> 🏠 Residential &nbsp;·&nbsp; '
            '<span style="color:#5fa8ff">●</span> A\'s customers '
            '<span style="color:#ff9d4d">●</span> B\'s <span style="color:#c4a8ff">●</span> tie</div>', unsafe_allow_html=True)
event = st.plotly_chart(fig, **_stretch_kw(st.plotly_chart), key=f"town_map_{st.session_state.get('_map_n', 0)}",
                        on_select="rerun", selection_mode="points")

points = []
try:
    points = event.selection.points if event is not None else []
except Exception:
    points = []
for point in reversed(points):
    cd = point.get("customdata")
    if cd and cd[0] == "grid":
        name = st.session_state.get("placing") or "A"
        st.session_state[name][0] = float(cd[1]); st.session_state[name][1] = float(cd[2])
        st.session_state["_needs_sync"] = True
        st.session_state["_map_n"] = st.session_state.get("_map_n", 0) + 1
        st.rerun()

if st.session_state.pop("_open_info", False):
    show_info()