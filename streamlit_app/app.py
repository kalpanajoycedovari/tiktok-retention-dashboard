"""
TikTok User Retention Dashboard — Streamlit App
Run: streamlit run streamlit_app/app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(
    page_title="TikTok Retention Dashboard",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Atkinson Hyperlegible', Arial, sans-serif !important;
    background-color: #ffffff !important;
    color: #111111 !important;
}

[data-testid="stSidebar"] {
    background-color: #f5f5f5 !important;
    border-right: 1px solid #e0e0e0;
}

h1, h2, h3, h4 {
    font-family: 'Atkinson Hyperlegible', Arial, sans-serif !important;
    color: #111111 !important;
}

.metric-card {
    background: #f9f9f9;
    border: 1px solid #e0e0e0;
    border-radius: 10px;
    padding: 20px;
    text-align: center;
}
.metric-label {
    color: #555555;
    font-size: 12px;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 6px;
    font-family: 'Atkinson Hyperlegible', Arial, sans-serif;
}
.metric-value {
    color: #111111;
    font-size: 30px;
    font-weight: 700;
    font-family: 'Atkinson Hyperlegible', Arial, sans-serif;
}
.metric-delta {
    font-size: 13px;
    margin-top: 4px;
    font-family: 'Atkinson Hyperlegible', Arial, sans-serif;
}
.delta-pos { color: #1a7a1a; }
.delta-neg { color: #cc0000; }

.section-title {
    font-family: 'Atkinson Hyperlegible', Arial, sans-serif !important;
    font-size: 18px;
    font-weight: 700;
    color: #111111;
    border-left: 4px solid #111111;
    padding-left: 12px;
    margin: 28px 0 16px 0;
}

[data-testid="stDataFrame"] {
    font-family: 'Atkinson Hyperlegible', Arial, sans-serif !important;
}
</style>
""", unsafe_allow_html=True)

# ── Load data ────────────────────────────────────────────────────────────────
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "tiktok_retention_data.csv")

@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH, parse_dates=["signup_date"])

try:
    df = load_data()
except FileNotFoundError:
    st.error("Dataset not found. Run `python data/generate_data.py` first.")
    st.stop()

# ── Chart theme ───────────────────────────────────────────────────────────────
CHART_COLORS = ["#2196F3", "#F44336", "#4CAF50", "#FF9800", "#9C27B0"]
LAYOUT = dict(
    paper_bgcolor="#ffffff",
    plot_bgcolor="#ffffff",
    font=dict(color="#111111", family="Atkinson Hyperlegible, Arial, sans-serif"),
    margin=dict(t=40, b=40, l=60, r=20),
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## Filters")
    segments  = st.multiselect("User Segment",         df["segment"].unique().tolist(),         default=df["segment"].unique().tolist())
    channels  = st.multiselect("Acquisition Channel",  df["acquisition_channel"].unique().tolist(), default=df["acquisition_channel"].unique().tolist())
    devices   = st.multiselect("Device",               df["device"].unique().tolist(),           default=df["device"].unique().tolist())
    countries = st.multiselect("Country",              df["country"].unique().tolist(),           default=df["country"].unique().tolist())
    date_range = st.date_input("Signup Date Range", value=(df["signup_date"].min(), df["signup_date"].max()))
    st.markdown("---")
    st.markdown(f"**Total users:** {len(df):,}")
    st.markdown("**Cohort period:** Jan–Dec 2024")
    st.markdown("**Observation window:** 90 days")

# ── Filter ────────────────────────────────────────────────────────────────────
fdf = df[
    df["segment"].isin(segments) &
    df["acquisition_channel"].isin(channels) &
    df["device"].isin(devices) &
    df["country"].isin(countries)
]
if len(date_range) == 2:
    fdf = fdf[
        (fdf["signup_date"] >= pd.Timestamp(date_range[0])) &
        (fdf["signup_date"] <= pd.Timestamp(date_range[1]))
    ]

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<h1 style='font-size:34px; color:#111111; margin-bottom:4px;'>
📱 TikTok User Retention Dashboard
</h1>
<p style='color:#555555; font-size:15px; margin-bottom:28px;'>
Cohort analysis · Churn curves · Feature impact · 50,000 users · Jan–Dec 2024
</p>
""", unsafe_allow_html=True)

# ── KPIs ──────────────────────────────────────────────────────────────────────
col1, col2, col3, col4, col5 = st.columns(5)
churn = fdf["churned"].mean()
d1    = fdf["d1_retained"].mean()
d7    = fdf["d7_retained"].mean()
d30   = fdf["d30_retained"].mean()

for col, label, val, delta, pos in zip(
    [col1, col2, col3, col4, col5],
    ["Total Users", "Churn Rate", "D1 Retention", "D7 Retention", "D30 Retention"],
    [f"{len(fdf):,}", f"{churn:.1%}", f"{d1:.1%}", f"{d7:.1%}", f"{d30:.1%}"],
    ["", "vs 42% baseline", "vs 65% baseline", "vs 40% baseline", "vs 25% baseline"],
    [True, churn < 0.42, d1 > 0.65, d7 > 0.40, d30 > 0.25],
):
    with col:
        delta_class = "delta-pos" if pos else "delta-neg"
        delta_icon  = "▲" if pos else "▼"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{val}</div>
            <div class="metric-delta {delta_class}">{delta_icon if delta else ""} {delta}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Cohort Heatmap ────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Cohort Retention Heatmap</div>', unsafe_allow_html=True)

cohort_grp = fdf.groupby("cohort_month").agg(
    cohort_size=("user_id", "count"),
    d1=("d1_retained", "mean"),
    d7=("d7_retained", "mean"),
    d30=("d30_retained", "mean"),
    churned=("churned", "mean"),
).reset_index().sort_values("cohort_month")

heatmap_data = cohort_grp.set_index("cohort_month")[["d1","d7","d30"]].T * 100
heatmap_data.index = ["Day 1", "Day 7", "Day 30"]

fig_heat = go.Figure(data=go.Heatmap(
    z=heatmap_data.values,
    x=heatmap_data.columns.tolist(),
    y=heatmap_data.index.tolist(),
    colorscale=[[0, "#ffffff"], [0.5, "#90CAF9"], [1, "#1565C0"]],
    text=np.round(heatmap_data.values, 1),
    texttemplate="%{text}%",
    textfont={"size": 12, "family": "Atkinson Hyperlegible, Arial"},
    zmin=0, zmax=100,
))
fig_heat.update_layout(**LAYOUT, height=220,
    xaxis=dict(tickangle=-45, gridcolor="#eeeeee"),
    yaxis=dict(gridcolor="#eeeeee"),
)
st.plotly_chart(fig_heat, use_container_width=True)

# ── Retention Curves ──────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Retention Curves by Segment & Channel</div>', unsafe_allow_html=True)
col_l, col_r = st.columns(2)

with col_l:
    seg_ret = fdf.groupby("segment")[["d1_retained","d7_retained","d30_retained"]].mean().reset_index()
    seg_ret_m = seg_ret.melt("segment", var_name="milestone", value_name="retention")
    seg_ret_m["milestone"] = seg_ret_m["milestone"].map({"d1_retained":"Day 1","d7_retained":"Day 7","d30_retained":"Day 30"})
    fig_seg = px.line(seg_ret_m, x="milestone", y="retention", color="segment",
                      markers=True, color_discrete_sequence=CHART_COLORS)
    fig_seg.update_layout(**LAYOUT, height=320,
        xaxis=dict(gridcolor="#eeeeee", title=""),
        yaxis=dict(gridcolor="#eeeeee", tickformat=".0%", title="Retention Rate"),
        title=dict(text="By Segment", font=dict(size=14)),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
    )
    fig_seg.update_traces(line_width=2.5, marker_size=8)
    st.plotly_chart(fig_seg, use_container_width=True)

with col_r:
    ch_ret = fdf.groupby("acquisition_channel")[["d1_retained","d7_retained","d30_retained"]].mean().reset_index()
    ch_ret_m = ch_ret.melt("acquisition_channel", var_name="milestone", value_name="retention")
    ch_ret_m["milestone"] = ch_ret_m["milestone"].map({"d1_retained":"Day 1","d7_retained":"Day 7","d30_retained":"Day 30"})
    fig_ch = px.line(ch_ret_m, x="milestone", y="retention", color="acquisition_channel",
                     markers=True, color_discrete_sequence=CHART_COLORS)
    fig_ch.update_layout(**LAYOUT, height=320,
        xaxis=dict(gridcolor="#eeeeee", title=""),
        yaxis=dict(gridcolor="#eeeeee", tickformat=".0%", title="Retention Rate"),
        title=dict(text="By Channel", font=dict(size=14)),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
    )
    fig_ch.update_traces(line_width=2.5, marker_size=8)
    st.plotly_chart(fig_ch, use_container_width=True)

# ── Churn Analysis ────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Churn Analysis</div>', unsafe_allow_html=True)
col_a, col_b, col_c = st.columns(3)

with col_a:
    churned_only = fdf[fdf["churned"] == 1]
    fig_cd = px.histogram(churned_only, x="days_until_churn", nbins=30,
                          color_discrete_sequence=["#F44336"])
    fig_cd.update_layout(**LAYOUT, height=280,
        xaxis=dict(gridcolor="#eeeeee", title="Days Until Churn"),
        yaxis=dict(gridcolor="#eeeeee", title="Users"),
        title=dict(text="Days to Churn Distribution", font=dict(size=13)),
        bargap=0.1,
    )
    st.plotly_chart(fig_cd, use_container_width=True)

with col_b:
    churn_seg = fdf.groupby("segment")["churned"].mean().reset_index().sort_values("churned")
    fig_cs = px.bar(churn_seg, x="churned", y="segment", orientation="h",
                    color="churned",
                    color_continuous_scale=["#4CAF50", "#FFEB3B", "#F44336"])
    fig_cs.update_layout(**LAYOUT, height=280,
        xaxis=dict(gridcolor="#eeeeee", tickformat=".0%", title="Churn Rate"),
        yaxis=dict(gridcolor="#eeeeee", title=""),
        title=dict(text="Churn Rate by Segment", font=dict(size=13)),
        coloraxis_showscale=False,
    )
    st.plotly_chart(fig_cs, use_container_width=True)

with col_c:
    churn_age = fdf.groupby("age_group")["churned"].mean().reset_index()
    age_order = ["13-17","18-24","25-34","35-44","45+"]
    churn_age["age_group"] = pd.Categorical(churn_age["age_group"], categories=age_order, ordered=True)
    churn_age = churn_age.sort_values("age_group")
    fig_ca = px.bar(churn_age, x="age_group", y="churned",
                    color="churned",
                    color_continuous_scale=["#4CAF50", "#FFEB3B", "#F44336"])
    fig_ca.update_layout(**LAYOUT, height=280,
        xaxis=dict(gridcolor="#eeeeee", title="Age Group"),
        yaxis=dict(gridcolor="#eeeeee", tickformat=".0%", title="Churn Rate"),
        title=dict(text="Churn Rate by Age Group", font=dict(size=13)),
        coloraxis_showscale=False,
    )
    st.plotly_chart(fig_ca, use_container_width=True)

# ── Feature Impact ────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Feature Impact on D30 Retention</div>', unsafe_allow_html=True)

features = ["used_fyp","used_search","used_live","used_shop","used_duet","notification_enabled"]
labels   = ["For You Page","Search","Live","Shop","Duet","Push Notifs"]

rows = []
for feat, label in zip(features, labels):
    with_f    = fdf[fdf[feat]==1]["d30_retained"].mean()
    without_f = fdf[fdf[feat]==0]["d30_retained"].mean()
    rows.append({"Feature": label, "With Feature": with_f, "Without Feature": without_f, "Lift": with_f - without_f})

impact_df = pd.DataFrame(rows).sort_values("Lift", ascending=True)

fig_feat = go.Figure()
fig_feat.add_trace(go.Bar(name="Without Feature", y=impact_df["Feature"],
                          x=impact_df["Without Feature"], orientation="h",
                          marker_color="#BDBDBD"))
fig_feat.add_trace(go.Bar(name="With Feature", y=impact_df["Feature"],
                          x=impact_df["With Feature"], orientation="h",
                          marker_color="#2196F3"))
fig_feat.update_layout(**LAYOUT, barmode="overlay", height=320,
    xaxis=dict(gridcolor="#eeeeee", tickformat=".0%", title="D30 Retention Rate"),
    yaxis=dict(gridcolor="#eeeeee"),
    legend=dict(bgcolor="rgba(0,0,0,0)"),
)
st.plotly_chart(fig_feat, use_container_width=True)

# ── Scatter ───────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Engagement vs Retention</div>', unsafe_allow_html=True)

sample = fdf.sample(min(3000, len(fdf)), random_state=42)
fig_sc = px.scatter(sample, x="total_sessions", y="total_watch_minutes",
                    color="segment", opacity=0.5,
                    color_discrete_sequence=CHART_COLORS,
                    labels={"total_sessions":"Total Sessions","total_watch_minutes":"Watch Time (min)"})
fig_sc.update_layout(**LAYOUT, height=380,
    xaxis=dict(gridcolor="#eeeeee"),
    yaxis=dict(gridcolor="#eeeeee"),
    legend=dict(bgcolor="rgba(0,0,0,0)"),
)
st.plotly_chart(fig_sc, use_container_width=True)

# ── Cohort Table ──────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Monthly Cohort Summary</div>', unsafe_allow_html=True)

cohort_display = cohort_grp.copy()
cohort_display["d1"]      = (cohort_display["d1"] * 100).round(1).astype(str) + "%"
cohort_display["d7"]      = (cohort_display["d7"] * 100).round(1).astype(str) + "%"
cohort_display["d30"]     = (cohort_display["d30"] * 100).round(1).astype(str) + "%"
cohort_display["churned"] = (cohort_display["churned"] * 100).round(1).astype(str) + "%"
cohort_display.columns    = ["Cohort Month","Cohort Size","D1 Retention","D7 Retention","D30 Retention","Churn Rate"]
st.dataframe(cohort_display, use_container_width=True, hide_index=True)

st.markdown("<br><p style='color:#aaaaaa; font-size:12px; text-align:center;'>TikTok Retention Dashboard · Synthetic Data · Built with Streamlit + Plotly</p>", unsafe_allow_html=True)