from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(
    page_title="SupeRR Selector | IPL 2027",
    page_icon="🏏",
    layout="wide"
)

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
RESULTS = ROOT / "results"
NOTEBOOKS = ROOT / "notebooks"

st.markdown("""
<style>
.stApp {background: #f7f7f8;}
[data-testid="stHeader"] {background: rgba(0,0,0,0);}
.hero {
    background: linear-gradient(110deg, #7b1530, #24111b);
    padding: 25px 30px;
    border-radius: 15px;
    color: white;
    margin-bottom: 18px;
}
.hero h1 {color: white; margin: 0;}
.hero p {color: #f5dce4; margin: 7px 0 0 0;}
.warning {
    background: #fff4df;
    border-left: 5px solid #d68b16;
    padding: 13px 16px;
    border-radius: 7px;
    color: #543b13;
    margin: 12px 0 20px 0;
}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_csv(path):
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


batting = load_csv(NOTEBOOKS / "improved_batting_rankings.csv")
bowling = load_csv(NOTEBOOKS / "improved_bowling_rankings.csv")
shortlist = load_csv(NOTEBOOKS / "final_top10_shortlist.csv")
pressure = load_csv(RESULTS / "pressure_summary.csv")
stages = load_csv(RESULTS / "stage_summary.csv")
validation = load_csv(RESULTS / "data_validation_summary.csv")
model_validation = load_csv(RESULTS / "model_validation_summary.csv")
season = load_csv(RESULTS / "season_analysis.csv")

st.markdown("""
<div class="hero">
    <h1>🏏 SupeRR Selector</h1>
    <p>Data-driven T20 performance analysis | Rajasthan Royals IPL 2027 Auction Strategy</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="warning">
<b>Important eligibility note:</b> These rankings are preliminary performance-model outputs.
The available dataset does not contain verified player date-of-birth and uncapped-status fields.
Therefore, the displayed names must not be treated as the final eligible list of youngest
uncapped domestic players until eligibility is independently verified.
</div>
""", unsafe_allow_html=True)

total_deliveries = 200999
bat_count = int(model_validation.loc[model_validation["Category"].str.lower() == "batters", "Eligible Players"].sum()) if not model_validation.empty else 0
bowl_count = int(model_validation.loc[model_validation["Category"].str.lower() == "bowlers", "Eligible Players"].sum()) if not model_validation.empty else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("Deliveries analysed", f"{total_deliveries:,}")
c2.metric("Eligible batters in model", f"{bat_count:,}")
c3.metric("Eligible bowlers in model", f"{bowl_count:,}")
c4.metric("Shortlist size", len(shortlist) if not shortlist.empty else 0)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏏 Batting Analysis",
    "🎯 Bowling Analysis",
    "⚡ Pressure Analysis",
    "📊 Dataset Overview",
    "ℹ️ Methodology"
])

with tab1:
    st.subheader("Top batting performers under pressure")
    if batting.empty:
        st.error("Missing file: notebooks/improved_batting_rankings.csv")
    else:
        top_n = st.slider("Number of batters to display", 5, min(30, len(batting)), 10, key="bat_n")
        bat_view = batting.sort_values("reliability_score", ascending=False).head(top_n)
        fig = px.bar(
            bat_view.sort_values("reliability_score"),
            x="reliability_score",
            y="striker_name",
            orientation="h",
            color="reliability_score",
            color_continuous_scale=["#e9b7c5", "#7b1530"],
            labels={"reliability_score": "Reliability score", "striker_name": "Player"}
        )
        fig.update_layout(height=max(400, top_n * 34), showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)
        cols = [c for c in [
            "rank", "striker_name", "runs", "balls", "dismissals", "innings",
            "batting_average", "strike_rate", "boundary_percentage",
            "dot_percentage", "reliability_score"
        ] if c in bat_view.columns]
        st.dataframe(bat_view[cols], use_container_width=True, hide_index=True)
        st.download_button(
            "Download batting rankings CSV",
            batting.to_csv(index=False).encode("utf-8"),
            "batting_rankings.csv",
            "text/csv"
        )

with tab2:
    st.subheader("Top bowling performers under pressure")
    if bowling.empty:
        st.error("Missing file: notebooks/improved_bowling_rankings.csv")
    else:
        top_n_b = st.slider("Number of bowlers to display", 5, min(30, len(bowling)), 10, key="bowl_n")
        bowl_view = bowling.sort_values("reliability_score", ascending=False).head(top_n_b)
        fig = px.bar(
            bowl_view.sort_values("reliability_score"),
            x="reliability_score",
            y="bowler_name",
            orientation="h",
            color="reliability_score",
            color_continuous_scale=["#b8c9df", "#193b68"],
            labels={"reliability_score": "Reliability score", "bowler_name": "Player"}
        )
        fig.update_layout(height=max(400, top_n_b * 34), showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)
        cols = [c for c in [
            "rank", "bowler_name", "wickets", "legal_balls", "dot_balls",
            "matches", "dot_percentage", "wicket_rate",
            "boundary_percentage", "reliability_score"
        ] if c in bowl_view.columns]
        st.dataframe(bowl_view[cols], use_container_width=True, hide_index=True)
        st.download_button(
            "Download bowling rankings CSV",
            bowling.to_csv(index=False).encode("utf-8"),
            "bowling_rankings.csv",
            "text/csv"
        )

with tab3:
    st.subheader("Performance across pressure levels and innings stages")
    left, right = st.columns(2)
    with left:
        if not pressure.empty:
            fig = px.bar(
                pressure,
                x="pressure_level",
                y="total_deliveries",
                color="pressure_level",
                title="Deliveries by pressure level",
                color_discrete_sequence=["#7b1530", "#c78b9e", "#d7a441", "#4b657d"]
            )
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(pressure, use_container_width=True, hide_index=True)
        else:
            st.info("Pressure summary file not found.")
    with right:
        if not stages.empty:
            fig = px.bar(
                stages,
                x="innings_stage",
                y="total_wickets",
                color="innings_stage",
                title="Wickets by innings stage",
                color_discrete_sequence=["#7b1530", "#d7a441", "#4b657d"]
            )
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(stages, use_container_width=True, hide_index=True)
        else:
            st.info("Stage summary file not found.")

with tab4:
    st.subheader("Dataset and model validation")
    if not validation.empty:
        st.markdown("**Data validation summary**")
        st.dataframe(validation, use_container_width=True, hide_index=True)
    if not model_validation.empty:
        st.markdown("**Model sample coverage**")
        st.dataframe(model_validation, use_container_width=True, hide_index=True)
    if not season.empty:
        st.markdown("**Matches by season and format**")
        fig = px.bar(
            season,
            x="season",
            y="total_matches",
            color="match_format",
            barmode="group",
            title="Matches included by season"
        )
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(season, use_container_width=True, hide_index=True)

with tab5:
    st.subheader("How to interpret this dashboard")
    st.markdown("""
**Batting model**
- Uses pressure-delivery batting performance.
- Composite reliability score combines batting average, strike rate,
  boundary percentage and dot-ball percentage.
- The ranking is a model score, not a probability of future success.

**Bowling model**
- Composite reliability score combines wicket rate, dot-ball percentage
  and boundary percentage conceded.
- The ranking is a model score, not a probability of future success.

**Important limitations**
1. The pressure score is a proxy based on innings stage and wickets lost.
   It does not fully model target, required run rate or balls remaining.
2. The dataset does not provide verified birth dates and uncapped status.
3. The shortlist therefore requires a separate eligibility check against
   the official competition rules before submission.
4. A high score should be reviewed with sample size and match context.
""")
    if not shortlist.empty:
        st.markdown("**Current preliminary top-10 shortlist**")
        st.dataframe(shortlist, use_container_width=True, hide_index=True)

st.caption("SupeRR Selector | Preliminary analytical dashboard | Verify eligibility before final submission")
