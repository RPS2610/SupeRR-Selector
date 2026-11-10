import pandas as pd
import numpy as np

INPUT_FILE = "advanced_pressure_analysis.csv"

df = pd.read_csv(INPUT_FILE)

required_columns = [
    "striker_id",
    "striker_name",
    "runs",
    "is_four",
    "is_six",
    "is_wicket",
    "dismissed_player_id",
    "extras_type",
    "pressure_level"
]

missing = [col for col in required_columns if col not in df.columns]

if missing:
    raise ValueError(f"Missing columns: {missing}")

for col in ["runs", "is_four", "is_six", "is_wicket"]:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

df["extras_type"] = df["extras_type"].fillna("").astype(str)

df["is_wide"] = df["extras_type"].str.contains(
    "wide", case=False, na=False
)

df["ball_faced"] = (~df["is_wide"]).astype(int)

df["is_dot"] = (
    (df["runs"] == 0) &
    (~df["is_wide"])
).astype(int)

df["is_batter_dismissal"] = (
    (df["is_wicket"] == 1) &
    (df["dismissed_player_id"] == df["striker_id"])
).astype(int)

pressure_df = df[
    df["pressure_level"].isin(["High", "Very High"])
].copy()

batting = (
    pressure_df.groupby(["striker_id", "striker_name"])
    .agg(
        runs=("runs", "sum"),
        balls=("ball_faced", "sum"),
        dismissals=("is_batter_dismissal", "sum"),
        fours=("is_four", "sum"),
        sixes=("is_six", "sum"),
        dot_balls=("is_dot", "sum"),
        innings=("match_id", "nunique")
    )
    .reset_index()
)

batting["batting_average"] = (
    batting["runs"] /
    batting["dismissals"].replace(0, np.nan)
)

batting["strike_rate"] = (
    batting["runs"] /
    batting["balls"].replace(0, np.nan)
) * 100

batting["boundary_percentage"] = (
    (batting["fours"] + batting["sixes"]) /
    batting["balls"].replace(0, np.nan)
) * 100

batting["dot_percentage"] = (
    batting["dot_balls"] /
    batting["balls"].replace(0, np.nan)
) * 100

batting = batting[
    (batting["balls"] >= 50) &
    (batting["innings"] >= 3)
].copy()

metrics = [
    "batting_average",
    "strike_rate",
    "boundary_percentage"
]

for metric in metrics:
    batting[metric + "_score"] = (
        batting[metric].rank(pct=True) * 100
    )

batting["dot_score"] = (
    (1 - batting["dot_percentage"].rank(pct=True)) * 100
)

batting["reliability_score"] = (
    batting["batting_average_score"] * 0.35 +
    batting["strike_rate_score"] * 0.25 +
    batting["boundary_percentage_score"] * 0.15 +
    batting["dot_score"] * 0.25
)

batting = batting.sort_values(
    "reliability_score", ascending=False
)

batting["rank"] = range(1, len(batting) + 1)

batting.to_csv("improved_batting_rankings.csv", index=False)

print("\nIMPROVED BATTING MODEL COMPLETED")
print("--------------------------------")

print(
    batting[
        [
            "rank",
            "striker_name",
            "runs",
            "balls",
            "batting_average",
            "strike_rate",
            "reliability_score"
        ]
    ].head(15).to_string(index=False)
)

print("\nFile generated: improved_batting_rankings.csv")
