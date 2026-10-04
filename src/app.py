import streamlit as st
import plotly.graph_objects as go
import numpy as np
import game as g
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
</style>
""", unsafe_allow_html=True)

if "placing" not in st.session_state:
    st.session_state.placing = "A"
if "A" not in st.session_state:
    st.session_state.A = [3, 5, 150, 4, 6]
if "B" not in st.session_state:
    st.session_state.B = [7, 5, 175, 4, 6]

def _sync_widgets():
    """Push strategy values into slider widget keys (must run before sliders are created)."""
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
    return [int(_snap(s[0], g.LOCS)), int(_snap(s[1], g.LOCS)), _snap(s[2], g.PRICES),
            _snap(s[3], g.QUALITIES), _snap(s[4], g.RADII)]

# Guard: snap strategies to values that exist in game.py (avoids KeyError)
st.session_state.A = _valid(st.session_state.A)
st.session_state.B = _valid(st.session_state.B)
A = tuple(st.session_state.A)
B = tuple(st.session_state.B)
res = g.evaluate(A, B)
na, nb = res["customers"]
pa, pb = res["profit"]

# ---------- Header ----------
st.markdown('<div class="hero"><div class="brand">SPATIAL <span>MARKET</span> · RESTAURANT GAME</div><div class="pill">SIMULATED TOWN · STRATEGIC MODE</div></div>', unsafe_allow_html=True)

# ---------- Restaurant strategy cards ----------
c1, c2, c3 = st.columns([1,1,1.3])
with c1:
    st.markdown(f'<div class="card"><div class="card-title">Restaurant A · {na:.0f} customers</div><div class="big a">₹{pa:,.0f}</div><div style="color:#7f8ea3">Profit · {na/N*100:.0f}% market share</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="card"><div class="card-title">Restaurant B · {nb:.0f} customers</div><div class="big b">₹{pb:,.0f}</div><div style="color:#7f8ea3">Profit · {nb/N*100:.0f}% market share</div></div>', unsafe_allow_html=True)
with c3:
    st.segmented_control("Place restaurant", ["A", "B"], key="placing", help="Choose a restaurant, then click anywhere on the town map to move it.")

# ---------- Controls ----------
left, right = st.columns(2)
for col, name, klass in [(left,"A","a"),(right,"B","b")]:
    with col:
        s = st.session_state[name]
        st.markdown(f'<div class="card"><div class="card-title">{name} · strategy</div>', unsafe_allow_html=True)
        q1,q2,q3 = st.columns(3)
        with q1: s[2] = st.select_slider("Price", g.PRICES, key=f"price_{name}")
        with q2: s[3] = st.select_slider("Quality", g.QUALITIES, key=f"quality_{name}")
        with q3: s[4] = st.select_slider("Delivery", g.RADII, key=f"radius_{name}", format_func=lambda x: f"{x} km")
        st.session_state[name] = s
        st.markdown('</div>', unsafe_allow_html=True)

A = tuple(st.session_state.A); B = tuple(st.session_state.B)
res = g.evaluate(A, B)
na, nb = res["customers"]; pa, pb = res["profit"]

# ---------- Map ----------
fig = go.Figure()

# Soft demand zones
for _, cx, cy, spread, n in g.ANCHORS:
    fig.add_shape(type="circle", x0=cx-spread*1.9, x1=cx+spread*1.9,
                  y0=cy-spread*1.9, y1=cy+spread*1.9,
                  fillcolor="rgba(120,140,190,.035)", line=dict(color="rgba(130,150,190,.10)", width=1), layer="below")

# Roads
for x in range(0, 11):
    fig.add_trace(go.Scatter(x=[x,x], y=[0,10], mode="lines", line=dict(color="rgba(100,115,140,.11)",width=1), hoverinfo="skip", showlegend=False))
for y in range(0, 11):
    fig.add_trace(go.Scatter(x=[0,10], y=[y,y], mode="lines", line=dict(color="rgba(100,115,140,.11)",width=1), hoverinfo="skip", showlegend=False))
fig.add_trace(go.Scatter(x=[0,10], y=[5,5], mode="lines", line=dict(color="rgba(115,160,255,.42)",width=5), hoverinfo="skip", showlegend=False))
fig.add_trace(go.Scatter(x=[5.5,5.5], y=[0,10], mode="lines", line=dict(color="rgba(255,120,120,.38)",width=3,dash="dot"), hoverinfo="skip", showlegend=False))

# Customers
w = res["a_wins"]
fig.add_trace(go.Scattergl(x=g.CX[w], y=g.CY[w], mode="markers", marker=dict(size=5,color="#5fa8ff",opacity=.58), hoverinfo="skip", showlegend=False))
fig.add_trace(go.Scattergl(x=g.CX[~w], y=g.CY[~w], mode="markers", marker=dict(size=5,color="#ff9d4d",opacity=.62), hoverinfo="skip", showlegend=False))

# Delivery rings
for s, color in [(A,"#5fa8ff"),(B,"#ff9d4d")]:
    fig.add_shape(type="circle", x0=s[0]-s[4], x1=s[0]+s[4], y0=s[1]-s[4], y1=s[1]+s[4],
                  line=dict(color=color,width=1,dash="dash"), fillcolor="rgba(0,0,0,0)")

# Restaurants
fig.add_trace(go.Scatter(x=[A[0]],y=[A[1]],mode="markers+text",text=["A"],textposition="middle center",
                         marker=dict(size=34,color="#5fa8ff",line=dict(color="#dbeafe",width=2)),
                         customdata=[["restaurant","A",A[0],A[1]]], hovertemplate="Restaurant A<br>Click to select<extra></extra>", showlegend=False))
fig.add_trace(go.Scatter(x=[B[0]],y=[B[1]],mode="markers+text",text=["B"],textposition="middle center",
                         marker=dict(size=34,color="#ff9d4d",line=dict(color="#ffedd5",width=2)),
                         customdata=[["restaurant","B",B[0],B[1]]], hovertemplate="Restaurant B<br>Click to select<extra></extra>", showlegend=False))

# Invisible placement grid. Click nearest grid cell; coordinates are deliberately hidden from UI.
grid_x=[]; grid_y=[]; grid_data=[]
for x in range(11):
    for y in range(11):
        grid_x.append(x); grid_y.append(y); grid_data.append(["grid",x,y])
fig.add_trace(go.Scatter(x=grid_x,y=grid_y,mode="markers",marker=dict(size=28,color="rgba(255,255,255,0.001)"),
                         customdata=grid_data, hoverinfo="skip", showlegend=False))

fig.update_layout(
    height=650,
    margin=dict(l=0,r=0,t=0,b=0),
    paper_bgcolor="#070b12", plot_bgcolor="#070b12",
    xaxis=dict(range=[0,10],visible=False,fixedrange=True),
    yaxis=dict(range=[0,10],visible=False,fixedrange=True,scaleanchor="x",scaleratio=1),
    showlegend=False,
    clickmode="event+select",
    dragmode=False,
)

st.markdown('<div style="margin:.65rem 0 .35rem;color:#718096;font-size:.76rem;letter-spacing:.13em;text-transform:uppercase">Live town map · choose A or B above, then click the map to place it</div>', unsafe_allow_html=True)
event = st.plotly_chart(fig, width='stretch', key="town_map", on_select="rerun", selection_mode="points")

# Handle map selection
try:
    points = event.selection.points if event is not None else []
    if points:
        point = points[-1]
        cd = point.get("customdata")
        if cd and cd[0] == "grid":
            name = st.session_state.placing
            st.session_state[name][0] = int(cd[1])
            st.session_state[name][1] = int(cd[2])
            st.rerun()
except Exception:
    pass

# ---------- Bottom sheet ----------
with st.expander("⌃  MORE INFO · PULL UP", expanded=False):
    st.markdown("### Game intelligence")
    m1,m2,m3,m4 = st.columns(4)
    m1.metric("Customers", f"{na:.0f} / {nb:.0f}", "A / B")
    m2.metric("Market share", f"{na/N*100:.0f}% / {nb/N*100:.0f}%", "A / B")
    m3.metric("Profit", f"₹{pa:,.0f} / ₹{pb:,.0f}", "A / B")
    m4.metric("Model", "Modified Hotelling")
    st.markdown("**How customers choose**  ·  Customers compare price, quality, road travel cost, and delivery availability. Road travel is asymmetric, so the shortest physical route is not always the cheapest route.")
    st.markdown("**Nash equilibrium**")
    bA,vA = g.best_response(0,B); bB,vB = g.best_response(1,A)
    is_eq = vA <= pa + 1e-9 and vB <= pb + 1e-9
    if is_eq:
        st.success("Current strategy is a Nash equilibrium: neither restaurant can improve profit through a unilateral change.")
    else:
        st.warning("Current strategy is not a Nash equilibrium. At least one restaurant has a profitable unilateral deviation.")
        st.write(f"A best response profit: ₹{vA:,.0f}  ·  B best response profit: ₹{vB:,.0f}")
    if st.button("Find equilibrium", type="secondary"):
        a,b,ok,h = g.find_nash(A,B)
        e=g.evaluate(a,b)
        st.session_state.A=list(a); st.session_state.B=list(b); st.session_state._needs_sync=True
        st.session_state.eq_result=(a,b,ok,e,len(h)-1)
        st.rerun()
    if "eq_result" in st.session_state:
        a,b,ok,e,moves=st.session_state.eq_result
        st.markdown(f"**Equilibrium search:** {'converged' if ok else 'cycle detected'} after {moves} moves · A serves {e['customers'][0]:.0f} · B serves {e['customers'][1]:.0f}")
