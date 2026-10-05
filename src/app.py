import streamlit as st
import plotly.graph_objects as go
import numpy as np
import os, importlib.util
import inspect as _inspect

# ---------------------------------------------------------------- engine loading
_GAME_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "game.py")

@st.cache_resource(show_spinner="Loading game engine (first start takes a few seconds)...")
def _load_engine(path, mtime):
    spec = importlib.util.spec_from_file_location("game_engine", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

st.set_page_config(page_title="Spatial Market | Restaurant Game", page_icon="🍽️", layout="wide",
                   initial_sidebar_state="collapsed")
g = _load_engine(_GAME_PATH, os.path.getmtime(_GAME_PATH))
if not hasattr(g, "ALL_ROADS"):
    st.error(f"The game.py at:\n\n{_GAME_PATH}\n\nis an OLD version. Replace it with the game.py from the zip, "
             "then restart Streamlit.")
    st.stop()
N = g.N_CUSTOMERS
W, H = g.TOWN_W, g.TOWN_H
HW = getattr(g, "HIGHWAYS", {})      # optional: highways (only if the engine defines them)
BR = g.BRIDGES

def road_name(rid):
    return (HW.get(rid) or BR.get(rid))[0]

def _stretch_kw(fn):
    params = _inspect.signature(fn).parameters
    if "width" in params:
        return {"width": "stretch"}
    return {"use_container_width": True} if "use_container_width" in params else {}

def _box():
    try:
        return st.container(border=True)
    except TypeError:
        return st.container()

# palette
CA, CB, CT = "#4cc9ff", "#ff8a3d", "#c4a8ff"          # A, B, tie
CHW, CBR, CGOLD, CGRN = "#a78bfa", "#f472b6", "#ffd666", "#6ee7a0"

# ---------------------------------------------------------------- theme
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&display=swap');
html, body, .stApp, [class*="css"] { font-family: 'Space Grotesk', 'Segoe UI', system-ui, sans-serif; }
:root { color-scheme: dark; }
.stApp {
  background:
    radial-gradient(900px 520px at 8% -8%, rgba(76,201,255,.22), transparent 60%),
    radial-gradient(900px 560px at 100% 0%, rgba(255,138,61,.18), transparent 58%),
    radial-gradient(700px 500px at 50% 115%, rgba(167,139,250,.20), transparent 60%),
    #05060f;
}
.stApp::before { content:""; position:fixed; inset:0; pointer-events:none; opacity:.35;
  background-image: radial-gradient(rgba(255,255,255,.55) 1px, transparent 1.2px);
  background-size: 46px 46px; animation: drift 60s linear infinite; }
@keyframes drift { to { background-position: 460px 460px; } }
[data-testid="stHeader"] { background: transparent; }
[data-testid="stSidebar"] { display:none; }
.block-container { max-width: 100% !important; padding: .8rem 1.4rem .6rem !important; }

/* hero */
.hero { display:flex; justify-content:space-between; align-items:center; margin:.1rem 0 .7rem; animation: fadeUp .7s ease both; }
.logo { font-size:2.05rem; font-weight:700; letter-spacing:.04em; line-height:1;
  background: linear-gradient(90deg,#4cc9ff,#a78bfa,#ff8a3d,#4cc9ff); background-size:300% 100%;
  -webkit-background-clip:text; background-clip:text; color:transparent; animation: shimmer 7s linear infinite; }
.tagline { color:#9aa6c4; font-size:.92rem; margin-top:.3rem; letter-spacing:.03em; }
.chips { display:flex; gap:.5rem; flex-wrap:wrap; }
.chip { border:1px solid rgba(255,255,255,.12); background:rgba(255,255,255,.04); padding:.35rem .75rem;
  border-radius:999px; color:#c4cde4; font-size:.76rem; backdrop-filter: blur(8px); }
.chip.live::before { content:"●"; color:#34d399; margin-right:.4rem; animation: blink 1.4s ease-in-out infinite; }
@keyframes shimmer { to { background-position: 300% 0; } }
@keyframes blink { 50% { opacity:.25; } }
@keyframes fadeUp { from { opacity:0; transform: translateY(14px);} to { opacity:1; transform:none; } }
@keyframes glowA { 50% { box-shadow: 0 0 36px rgba(76,201,255,.45), inset 0 0 22px rgba(76,201,255,.10);} }
@keyframes glowB { 50% { box-shadow: 0 0 36px rgba(255,138,61,.45), inset 0 0 22px rgba(255,138,61,.10);} }
@keyframes bob { 50% { transform: translateY(-4px) rotate(-6deg);} }

/* scoreboard */
.score { display:grid; grid-template-columns: 1fr 1.25fr 1fr; gap:14px; align-items:stretch; animation: fadeUp .8s .05s ease both; }
.team { position:relative; border-radius:22px; padding:14px 20px; background:rgba(255,255,255,.035);
  border:1px solid rgba(255,255,255,.10); backdrop-filter: blur(12px); overflow:hidden; }
.team::after { content:""; position:absolute; inset:0; pointer-events:none; opacity:.9;
  background: radial-gradient(260px 110px at 0% 0%, var(--c), transparent 70%); mix-blend-mode:soft-light; }
.team.a { --c: rgba(76,201,255,.55); border-color: rgba(76,201,255,.45); }
.team.b { --c: rgba(255,138,61,.55); border-color: rgba(255,138,61,.45); text-align:right; }
.team.lead.a { animation: glowA 2.6s ease-in-out infinite; }
.team.lead.b { animation: glowB 2.6s ease-in-out infinite; }
.tag { font-size:.72rem; letter-spacing:.22em; color:#9aa6c4; text-transform:uppercase; }
.crown { display:inline-block; animation: bob 2s ease-in-out infinite; }
.profit { font-size:2.15rem; font-weight:700; line-height:1.15; margin:.1rem 0; position:relative; z-index:1; }
.team.a .profit { color:#4cc9ff; text-shadow:0 0 22px rgba(76,201,255,.55); }
.team.b .profit { color:#ff8a3d; text-shadow:0 0 22px rgba(255,138,61,.55); }
.sub { color:#9aa6c4; font-size:.86rem; position:relative; z-index:1; }
.vs { border-radius:22px; padding:12px 18px; background:rgba(255,255,255,.03); border:1px solid rgba(255,255,255,.08);
  display:flex; flex-direction:column; justify-content:center; gap:8px; backdrop-filter: blur(12px); }
.vs-top { display:flex; justify-content:space-between; font-size:.74rem; letter-spacing:.18em; color:#9aa6c4; }
.bar { height:16px; border-radius:99px; overflow:hidden; background:linear-gradient(90deg,#ff8a3d,#ff5d8f); position:relative;
  box-shadow: 0 0 20px rgba(167,139,250,.25); }
.bar .fa { height:100%; background:linear-gradient(90deg,#29d3ff,#4cc9ff); border-radius:99px; transition: width .9s cubic-bezier(.2,.9,.2,1);
  box-shadow: 0 0 18px rgba(76,201,255,.8); }
.bar .mid { position:absolute; left:50%; top:0; bottom:0; width:2px; background:rgba(255,255,255,.55); }
.vs-share { display:flex; justify-content:space-between; font-weight:700; font-size:1.15rem; }
.vs-share .l { color:#4cc9ff; } .vs-share .r { color:#ff8a3d; }
.note { color:#c4cde4; font-size:.82rem; text-align:center; min-height:1.1em; }

/* glass containers (map + control panel) */
[data-testid="stVerticalBlockBorderWrapper"] { border-radius:22px !important; border:1px solid rgba(255,255,255,.10) !important;
  background: rgba(10,14,32,.62) !important; backdrop-filter: blur(14px); box-shadow: 0 18px 50px rgba(0,0,0,.45); }
.panel-title { color:#9aa6c4; font-size:.7rem; letter-spacing:.22em; text-transform:uppercase; margin:.2rem 0 .35rem; }
.legend { display:flex; flex-wrap:wrap; gap:.45rem; margin:.35rem 0 .1rem; }
.legend span { font-size:.76rem; color:#c4cde4; border:1px solid rgba(255,255,255,.10); background:rgba(255,255,255,.035);
  padding:.22rem .6rem; border-radius:99px; }
.mode-hint { color:#a78bfa; font-size:.74rem; letter-spacing:.14em; text-transform:uppercase; margin:.1rem 0 .4rem; }

/* widgets */
button[kind="primary"] { background: linear-gradient(90deg,#6d5efc,#c026d3) !important; border:0 !important; border-radius:14px !important;
  font-weight:700 !important; box-shadow: 0 0 26px rgba(168,85,247,.5); transition: transform .15s, box-shadow .15s; }
button[kind="primary"]:hover { transform: translateY(-2px) scale(1.02); box-shadow: 0 0 40px rgba(192,38,211,.8); }
button[kind="secondary"] { border-radius:14px !important; background:rgba(255,255,255,.05) !important; border:1px solid rgba(255,255,255,.14) !important; }
button[kind="secondary"]:hover { border-color: rgba(167,139,250,.8) !important; box-shadow: 0 0 18px rgba(167,139,250,.35); }
[data-baseweb="tab-list"] { gap:6px; }
[data-baseweb="tab"] { border-radius:12px 12px 0 0; }
[data-testid="stMetric"] { background:rgba(255,255,255,.04); border:1px solid rgba(255,255,255,.10); border-radius:16px; padding:10px 12px; }
@keyframes slideUp { from {transform:translateY(60px);opacity:0} to {transform:translateY(0);opacity:1} }
div[data-testid="stDialog"] div[role="dialog"] { animation: slideUp .45s cubic-bezier(.2,.8,.2,1); border-radius:24px;
  border:1px solid rgba(167,139,250,.4); box-shadow: 0 0 60px rgba(124,58,237,.35); }

/* welcome cards */
.wc { display:grid; grid-template-columns: repeat(3, 1fr); gap:12px; margin:.6rem 0; }
.wc div { background:rgba(255,255,255,.05); border:1px solid rgba(255,255,255,.12); border-radius:18px; padding:14px; animation: fadeUp .6s both; }
.wc div:nth-child(2){ animation-delay:.12s } .wc div:nth-child(3){ animation-delay:.24s }
.wc b { display:block; font-size:1.7rem; } .wc span { color:#c4cde4; font-size:.86rem; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------- state
st.session_state.setdefault("placing", "A")
st.session_state.setdefault("A", [6.0, 5.0, 150, 4, 6])
st.session_state.setdefault("B", [14.0, 5.0, 175, 4, 6])
st.session_state.setdefault("closed", set())
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

# ---------------------------------------------------------------- map helpers
def zone_text(x, y, closed=()):
    z = []
    for rid, (nm, hy) in HW.items():
        if abs(y - hy) <= 0.25:
            z.append(f"⛔ {nm} · CLOSED" if rid in closed else f"🛣️ {nm} · fastest roads")
    for rid, (nm, bx) in BR.items():
        if bx <= x <= bx + 1:
            z.append(f"⛔ {nm} · CLOSED" if rid in closed else f"🌉 {nm} · bottleneck")
    names = {"Town centre": "🏙️ Town centre · dense demand", "Shopping mall": "🛍️ Shopping mall · demand hub",
             "Business district": "🏢 Business district · demand hub"}
    for nm, cx, cy, sp, _n in g.ANCHORS:
        if np.hypot(x - cx, y - cy) <= sp * 1.6: z.append(names[nm])
    for nm, cx, cy, sp, _n in g.RESIDENTIAL:
        if np.hypot(x - cx, y - cy) <= sp * 1.6: z.append(f"🏠 {nm} · residential area")
    return "<br>".join(z) if z else "Free area · open land"

@st.cache_data
def click_layer(closed=()):
    gx, gy, gd = [], [], []
    for x in np.arange(0, W + 1e-9, 0.25):
        for y in np.arange(0, H + 1e-9, 0.25):
            gx.append(float(x)); gy.append(float(y)); gd.append(["grid", float(x), float(y), zone_text(x, y, closed)])
    return gx, gy, gd

def road_layer(closed):
    rx, ry, rd = [], [], []
    def tip(nm, rid):
        return f"{nm} · {'CLOSED' if rid in closed else 'open'}<br><i>click to {'reopen' if rid in closed else 'close'}</i>"
    for rid, (nm, hy) in HW.items():
        for x in np.arange(0.25, W, 0.5):
            rx.append(float(x)); ry.append(float(hy)); rd.append(["road", rid, 0, tip(nm, rid)])
    for rid, (nm, bx) in BR.items():
        for y in np.arange(0.25, H, 0.5):
            rx.append(bx + 0.5); ry.append(float(y)); rd.append(["road", rid, 0, tip(nm, rid)])
    return rx, ry, rd

def glow_line(fig, xs, ys, color_rgb, widths=((22, .05), (11, .12), (4, .95)), dash=None):
    for wd, al in widths:
        fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", hoverinfo="skip", showlegend=False,
                                 line=dict(color=f"rgba({color_rgb},{al})", width=wd, dash=dash or "solid")))

def halo(fig, x, y, rgb, sizes=((70, .07), (52, .12), (38, .18))):
    for sz, al in sizes:
        fig.add_trace(go.Scatter(x=x, y=y, mode="markers", hoverinfo="skip", showlegend=False,
                                 marker=dict(size=sz, color=f"rgba({rgb},{al})")))

FONT = "Space Grotesk, Segoe UI, sans-serif"

def build_map(A, B, res, CLOSED, mode):
    fig = go.Figure()
    # town: glowing frame
    fig.add_shape(type="rect", x0=0, x1=W, y0=0, y1=H, fillcolor="#0a1026", line=dict(width=0), layer="below")
    bx_, by_ = [0, W, W, 0, 0], [0, 0, H, H, 0]
    glow_line(fig, bx_, by_, "124,131,255", widths=((18, .05), (9, .12), (2.5, .85)))
    fig.add_annotation(x=0.25, y=H-0.2, text="<b>T O W N</b>", showarrow=False, xanchor="left", yanchor="top",
                       font=dict(size=12, color="rgba(170,185,235,.8)", family=FONT))

    # customers: soft territory halo + crisp dots
    wv = res["w"]
    for mask, rgb, hexc in ((wv == 1, "76,201,255", CA), (wv == 0, "255,138,61", CB), (wv == 0.5, "196,168,255", CT)):
        if mask.any():
            fig.add_trace(go.Scattergl(x=g.CX[mask], y=g.CY[mask], mode="markers", hoverinfo="skip", showlegend=False,
                                       marker=dict(size=24, color=f"rgba({rgb},.06)")))
            fig.add_trace(go.Scattergl(x=g.CX[mask], y=g.CY[mask], mode="markers", hoverinfo="skip", showlegend=False,
                                       marker=dict(size=8, color=hexc, opacity=.92)))

    # bridges
    for k, (rid, (nm, bx)) in enumerate(BR.items()):
        cl = rid in CLOSED
        if cl:
            fig.add_shape(type="rect", x0=bx+0.15, x1=bx+0.85, y0=0, y1=H, fillcolor="rgba(30,10,16,.92)",
                          line=dict(color="rgba(255,70,90,.95)", width=2), layer="below")
            ys_ = np.arange(0.6, H, 1.2)
            fig.add_trace(go.Scatter(x=[bx+0.5]*len(ys_), y=ys_, mode="text", text=["✕"]*len(ys_), hoverinfo="skip",
                                     showlegend=False, textfont=dict(size=13, color="rgba(255,90,110,.9)")))
        else:
            fig.add_shape(type="rect", x0=bx+0.15, x1=bx+0.85, y0=0, y1=H, fillcolor="rgba(244,114,182,.08)",
                          line=dict(width=0), layer="below")
            for xx in (bx+0.15, bx+0.85):
                glow_line(fig, [xx, xx], [0, H], "244,114,182", widths=((12, .06), (6, .14), (2, .9)))
        fig.add_annotation(x=bx+0.5, y=0.55 if k % 2 == 0 else H-0.55, showarrow=False,
                           text=(f"⛔ <b>{nm}</b><br>CLOSED" if cl else f"🌉 <b>{nm}</b><br>slow crossing"),
                           font=dict(size=10, family=FONT, color="#ff6b81" if cl else "#fbcfe8"),
                           bgcolor="rgba(8,10,24,.92)", bordercolor="rgba(255,90,110,.8)" if cl else "rgba(244,114,182,.7)",
                           borderwidth=1, borderpad=3)

    # highways
    for rid, (nm, hy) in HW.items():
        cl = rid in CLOSED
        if cl:
            fig.add_shape(type="rect", x0=0, x1=W, y0=hy-0.22, y1=hy+0.22, fillcolor="rgba(120,120,135,.12)",
                          line=dict(width=0), layer="below")
            glow_line(fig, [0, W], [hy, hy], "255,90,110", widths=((3, .65),), dash="dot")
        else:
            fig.add_shape(type="rect", x0=0, x1=W, y0=hy-0.22, y1=hy+0.22, fillcolor="rgba(167,139,250,.10)",
                          line=dict(width=0), layer="below")
            glow_line(fig, [0, W], [hy, hy], "167,139,250", widths=((20, .05), (10, .11), (3, .85)), dash="dash")
        n_ = int(W / 1.2)
        fig.add_trace(go.Scatter(x=[0.7+1.2*i for i in range(n_)], y=[hy]*n_, mode="text", hoverinfo="skip",
                                 showlegend=False, text=["✕" if cl else "»"]*n_,
                                 textfont=dict(size=13 if cl else 16, color="rgba(255,90,110,.8)" if cl else "rgba(221,214,254,.9)")))
        fig.add_annotation(x=W-0.2, y=hy+0.5, xanchor="right", showarrow=False,
                           text=(f"⛔ {nm} · CLOSED" if cl else f"🛣️ {nm} · fast lane"),
                           font=dict(size=11, family=FONT, color="#ff6b81" if cl else "#ddd6fe"))

    # demand hubs (gold) and residential (green): halo + marker + framed label
    hub_icon = {"Town centre": "🏙️", "Shopping mall": "🛍️", "Business district": "🏢"}
    hx, hy_ = [h[1] for h in g.ANCHORS], [h[2] for h in g.ANCHORS]
    halo(fig, hx, hy_, "255,214,102", sizes=((74, .06), (54, .10), (38, .16)))
    fig.add_trace(go.Scatter(x=hx, y=hy_, mode="markers", hoverinfo="skip", showlegend=False,
                             marker=dict(symbol="diamond", size=15, color=CGOLD, line=dict(color="#fff7d6", width=2))))
    for nm, cx, cy, sp, _n in g.ANCHORS:
        fig.add_annotation(x=cx, y=cy, yshift=30, showarrow=False, text=f"{hub_icon[nm]} <b>{nm}</b>",
                           font=dict(size=11, color="#ffe9a8", family=FONT), bgcolor="rgba(45,34,6,.9)",
                           bordercolor="rgba(255,214,102,.8)", borderwidth=1, borderpad=4)
    rx, ry = [r[1] for r in g.RESIDENTIAL], [r[2] for r in g.RESIDENTIAL]
    halo(fig, rx, ry, "110,231,160", sizes=((58, .06), (42, .10), (30, .16)))
    fig.add_trace(go.Scatter(x=rx, y=ry, mode="markers", hoverinfo="skip", showlegend=False,
                             marker=dict(symbol="square", size=12, color=CGRN, line=dict(color="#e1ffee", width=2))))
    for nm, cx, cy, sp, _n in g.RESIDENTIAL:
        fig.add_annotation(x=cx, y=cy, yshift=-26, showarrow=False, text=f"🏠 {nm}",
                           font=dict(size=10, color="#c9f5d9", family=FONT), bgcolor="rgba(8,34,20,.9)",
                           bordercolor="rgba(110,231,160,.7)", borderwidth=1, borderpad=3)

    # restaurants: glowing orbs (side by side if they overlap), crown on the leader
    same = abs(A[0]-B[0]) < 0.7 and abs(A[1]-B[1]) < 0.7
    off = 0.38 if same else 0.0
    na_, nb_ = res["customers"]
    for s_, nm, rgb, col, dx, lead in ((A, "A", "76,201,255", CA, -off, na_ > nb_), (B, "B", "255,138,61", CB, off, nb_ > na_)):
        halo(fig, [s_[0]+dx], [s_[1]], rgb, sizes=((92, .07), (68, .12), (50, .20)))
        fig.add_trace(go.Scatter(x=[s_[0]+dx], y=[s_[1]], mode="markers+text", text=[f"<b>{nm}</b>"],
                                 textposition="middle center", hoverinfo="skip", showlegend=False,
                                 marker=dict(size=34, color=col, line=dict(color="#ffffff", width=2.5)),
                                 textfont=dict(color="#050814", size=15, family=FONT)))
        if lead:
            fig.add_annotation(x=s_[0]+dx, y=s_[1], yshift=34, text="👑", showarrow=False, font=dict(size=18))

    # invisible click layer
    gx, gy, gd = road_layer(CLOSED) if mode == "Roads" else click_layer(tuple(sorted(CLOSED)))
    fig.add_trace(go.Scatter(x=gx, y=gy, mode="markers", marker=dict(size=14, color="rgba(255,255,255,0.01)"),
                             customdata=gd, hovertemplate="%{customdata[3]}<extra></extra>",
                             hoverlabel=dict(bgcolor="#0e1430", bordercolor="#7c83ff", font=dict(color="#e8ecff", size=12, family=FONT)),
                             showlegend=False))
    PAD = 0.45
    fig.update_layout(height=585, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      xaxis=dict(range=[-PAD, W+PAD], visible=False, fixedrange=True),
                      yaxis=dict(range=[-PAD, H+PAD], visible=False, fixedrange=True),
                      showlegend=False, clickmode="event+select", dragmode=False, hovermode="closest", hoverdistance=-1)
    return fig

# ---------------------------------------------------------------- dialogs
_dlg = getattr(st, "dialog", None) or getattr(st, "experimental_dialog", None)

def _info_body():
    A_, B_ = tuple(st.session_state.A), tuple(st.session_state.B)
    r = g.evaluate(A_, B_); na_, nb_ = r["customers"]; pa_, pb_ = r["profit"]
    m1, m2, m3 = st.columns(3)
    m1.metric("Customers", f"{na_:.0f} / {nb_:.0f}", "A / B")
    m2.metric("Market share", f"{na_/N*100:.0f}% / {nb_/N*100:.0f}%", "A / B")
    m3.metric("Profit", f"₹{pa_:,.0f} / ₹{pb_:,.0f}", "A / B")
    cl = [ road_name(k) for k in g.ALL_ROADS if k in st.session_state.closed]
    st.markdown("**Roads:** " + ("all open" if not cl else "closed → " + ", ".join(cl)))
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
                 + (f"Search converged after {moves} moves." if ok else
                    f"Search entered a cycle after {moves} moves (no pure equilibrium found)."))
        if ok:
            st.write(f"🔵 A → price ₹{a[2]}, quality {a[3]}, delivery {a[4]} km · serves {e['customers'][0]:.0f}")
            st.write(f"🟠 B → price ₹{b[2]}, quality {b[3]}, delivery {b[4]} km · serves {e['customers'][1]:.0f}")
            if abs(a[0]-b[0]) < 0.7 and abs(a[1]-b[1]) < 0.7:
                st.info("Both restaurants chose the same spot (they appear side by side on the map).")
        else:
            st.error("No pure-strategy Nash equilibrium found: best responses keep cycling. "
                     "Your restaurants were left where you placed them.")

def _welcome_body():
    st.markdown("### Two restaurants. One town. Who wins the crowd?")
    st.markdown("""
<div class="wc">
<div><b>📍</b><span><strong>Place</strong><br>Pick <em>Place A</em> or <em>Place B</em>, then click anywhere on the map.</span></div>
<div><b>💰</b><span><strong>Compete</strong><br>Tune price, quality and delivery. Watch customers switch sides live.</span></div>
<div><b>🚧</b><span><strong>Disrupt</strong><br>Close highways or bridges and see the market reshape.</span></div>
</div>""", unsafe_allow_html=True)
    st.caption("Tip: press **Check equilibrium** to see where rational owners end up (Nash equilibrium).")
    if st.button("🚀 Start playing", type="primary"):
        st.rerun()

if _dlg:
    show_info = _dlg("Game intelligence")(_info_body)
    show_welcome = _dlg("Welcome to Spatial Market")(_welcome_body)
else:
    def show_info():
        with st.expander("Game intelligence", expanded=True):
            _info_body()
    def show_welcome():
        pass

# ---------------------------------------------------------------- layout
st.markdown('<div class="hero"><div><div class="logo">SPATIAL MARKET</div>'
            '<div class="tagline">The restaurant location game · Hotelling meets the real world</div></div>'
            '<div class="chips"><span class="chip live">LIVE SIMULATION</span>'
            f'<span class="chip">👥 {N:,} simulated customers</span><span class="chip">Nash equilibrium engine</span></div></div>',
            unsafe_allow_html=True)
score_ph = st.empty()
map_col, ctl_col = st.columns([3.3, 1.25], gap="medium")

# ---- control panel (rendered first so the scoreboard/map see the updated values)
with ctl_col:
    with _box():
        st.markdown('<div class="panel-title">Click mode</div>', unsafe_allow_html=True)
        st.segmented_control("Click mode", ["A", "B", "Roads"], key="placing", label_visibility="collapsed",
                             format_func=lambda v: {"A": "📍 Place A", "B": "📍 Place B", "Roads": "🚧 Roads"}[v],
                             help="Place A / Place B: click the map to put that restaurant there. "
                                  "Roads: click a highway or bridge to close or reopen it.")
        st.markdown('<div class="panel-title" style="margin-top:.6rem">Strategies</div>', unsafe_allow_html=True)
        tabA, tabB = st.tabs(["🔵 Restaurant A", "🟠 Restaurant B"])
        for tab, name in ((tabA, "A"), (tabB, "B")):
            with tab:
                s = st.session_state[name]
                s[2] = st.select_slider("Price (₹)", g.PRICES, key=f"price_{name}")
                s[3] = st.select_slider("Quality (★)", g.QUALITIES, key=f"quality_{name}")
                s[4] = st.select_slider("Delivery radius", g.RADII, key=f"radius_{name}", format_func=lambda x: f"{x} km")
                st.session_state[name] = s

        st.markdown('<div class="panel-title" style="margin-top:.4rem">Roads · switch off to close</div>', unsafe_allow_html=True)
        _ver = st.session_state.get("_road_ver", 0)
        _new_closed = set()
        for _rid in g.ALL_ROADS:
            _nm = road_name(_rid)
            _icon = "🛣️" if _rid in HW else "🌉"
            if not st.toggle(f"{_icon} {_nm}", value=_rid not in st.session_state.closed, key=f"road_{_rid}_{_ver}"):
                _new_closed.add(_rid)
        st.session_state.closed = _new_closed
        if g.CLOSED != frozenset(_new_closed):
            with st.spinner("Updating roads (about 2 seconds)..."):
                g.set_closed(_new_closed)
        CLOSED = set(_new_closed)

        st.markdown('<div style="height:.3rem"></div>', unsafe_allow_html=True)
        b1, b2 = st.columns(2)
        if b1.button("ℹ️ Game info", **_stretch_kw(st.button)):
            show_info()
        eq_clicked = b2.button("🔍 Equilibrium", type="primary", **_stretch_kw(st.button))

A = tuple(st.session_state.A); B = tuple(st.session_state.B)
res = g.evaluate(A, B)
na, nb = res["customers"]; pa, pb = res["profit"]

if eq_clicked:
    with st.spinner("Searching for equilibrium (about 15-30 seconds)..."):
        was_nash = g.is_nash(A, B)
        a, b, ok, h = g.find_nash(A, B)
        e = g.evaluate(a, b)
    if ok:
        st.session_state.A = list(a); st.session_state.B = list(b)
        st.session_state._needs_sync = True
    st.session_state._map_n = st.session_state.get("_map_n", 0) + 1
    st.session_state.eq_result = (a, b, ok, e, len(h) - 1, was_nash)
    st.session_state._open_info = True
    st.session_state._celebrate = bool(ok)
    st.rerun()

# ---- scoreboard
sa_, sb_ = na / N * 100, nb / N * 100
wv = res["w"]; west = g.CX < (W / 2)
pw = wv[west].mean() * 100; pe = wv[~west].mean() * 100
if abs(na - nb) < 1:
    note = "⚖️ Dead heat: the market is split evenly"
elif pw > 60 and pe < 40:
    note = f"🔵 A owns the west ({pw:.0f}%) · 🟠 B owns the east ({100-pe:.0f}%)"
elif pe > 60 and pw < 40:
    note = f"🟠 B owns the west ({100-pw:.0f}%) · 🔵 A owns the east ({pe:.0f}%)"
else:
    lead_ = "A" if na > nb else "B"
    note = f"{'🔵' if lead_ == 'A' else '🟠'} {lead_} leads by {abs(na-nb):.0f} customers"
if CLOSED:
    note += f" · ⛔ {len(CLOSED)} road{'s' if len(CLOSED) > 1 else ''} closed"
la, lb = ("lead" if na > nb else ""), ("lead" if nb > na else "")
score_ph.markdown(f"""
<div class="score">
  <div class="team a {la}"><div class="tag">Restaurant A {'<span class="crown">👑</span>' if la else ''}</div>
    <div class="profit">₹{pa:,.0f}</div><div class="sub">{na:.0f} customers · price ₹{A[2]} · quality {A[3]}★</div></div>
  <div class="vs"><div class="vs-top"><span>MARKET SHARE</span><span>VS</span></div>
    <div class="bar"><div class="fa" style="width:{sa_:.1f}%"></div><div class="mid"></div></div>
    <div class="vs-share"><span class="l">{sa_:.0f}%</span><span class="r">{sb_:.0f}%</span></div>
    <div class="note">{note}</div></div>
  <div class="team b {lb}"><div class="tag">{'<span class="crown">👑</span>' if lb else ''} Restaurant B</div>
    <div class="profit">₹{pb:,.0f}</div><div class="sub">{nb:.0f} customers · price ₹{B[2]} · quality {B[3]}★</div></div>
</div>""", unsafe_allow_html=True)

# ---- map
mode = st.session_state.get("placing") or "A"
with map_col:
    with _box():
        hint = ("🚧 Roads mode · click a highway or a bridge to close / reopen it" if mode == "Roads"
                else f"📍 Placing restaurant {mode} · click anywhere in the town · hover to explore")
        st.markdown(f'<div class="mode-hint">{hint}</div>', unsafe_allow_html=True)
        fig = build_map(A, B, res, CLOSED, mode)
        event = st.plotly_chart(fig, **_stretch_kw(st.plotly_chart), key=f"town_map_{st.session_state.get('_map_n', 0)}",
                                on_select="rerun", selection_mode="points")
        st.markdown(
            '<div class="legend">'
            + (f'<span><b style="color:{CHW}">━</b> 🛣️ Highway · fast</span>' if HW else '') +
            f'<span><b style="color:{CBR}">┃</b> 🌉 Bridge · slow</span><span>⛔ Closed</span>'
            f'<span><b style="color:{CGOLD}">◆</b> 🏙️🛍️🏢 Demand hubs</span>'
            f'<span><b style="color:{CGRN}">■</b> 🏠 Homes</span>'
            f'<span><b style="color:{CA}">●</b> A\'s customers</span><span><b style="color:{CB}">●</b> B\'s customers</span>'
            f'<span><b style="color:{CT}">●</b> Tie</span></div>', unsafe_allow_html=True)

points = []
try:
    points = event.selection.points if event is not None else []
except Exception:
    points = []
for point in reversed(points):
    cd = point.get("customdata")
    if cd and cd[0] == "road":
        _c = set(st.session_state.closed)
        _c.symmetric_difference_update({cd[1]})
        st.session_state.closed = _c
        st.session_state["_road_ver"] = st.session_state.get("_road_ver", 0) + 1
        st.session_state["_map_n"] = st.session_state.get("_map_n", 0) + 1
        st.rerun()
    if cd and cd[0] == "grid":
        name = mode if mode in ("A", "B") else "A"
        st.session_state[name][0] = float(cd[1]); st.session_state[name][1] = float(cd[2])
        st.session_state["_needs_sync"] = True
        st.session_state["_map_n"] = st.session_state.get("_map_n", 0) + 1
        st.rerun()

# ---- popups
if st.session_state.pop("_open_info", False):
    if st.session_state.pop("_celebrate", False):
        st.balloons()
    show_info()
elif _dlg and not st.session_state.get("_welcomed"):
    st.session_state["_welcomed"] = True
    show_welcome()