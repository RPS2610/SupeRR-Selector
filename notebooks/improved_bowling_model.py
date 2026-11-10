import pandas as pd
import numpy as np

df = pd.read_csv("advanced_pressure_analysis.csv")

required = [
    "bowler_id", "bowler_name", "match_id",
    "runs", "is_four", "is_six", "is_wicket",
    "dismissal_type", "extras_type", "pressure_level"
]

missing = [col for col in required if col not in df.columns]

if missing:
    raise ValueError(f"Missing columns: {missing}")

for col in ["runs", "is_four", "is_six", "is_wicket"]:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

df["extras_type"] = df["extras_type"].fillna("").astype(str)
df["dismissal_type"] = df["dismissal_type"].fillna("").astype(str)

pressure = df[
    df["pressure_level"].isin(["High", "Very High"])
].copy()

pressure["is_wide"] = pressure["extras_type"].str.contains(
    "wide", case=False, na=False
)

pressure["is_noball"] = pressure["extras_type"].str.contains(
    "no.?ball|noball|overstep", case=False, na=False
)

pressure["legal_ball"] = (
    ~pressure["is_wide"] & ~pressure["is_noball"]
).astype(int)

pressure["dot_ball"] = (
    (pressure["runs"] == 0) &
    (pressure["is_wide"] == False) &
    (pressure["is_noball"] == False)
).astype(int)

not_bowler_wicket = pressure["dismissal_type"].str.contains(
    "run out|retired hurt|retired out|obstructing the field",
    case=False,
    na=False
)

pressure["bowler_wicket"] = (
    (pressure["is_wicket"] == 1) &
    (~not_bowler_wicket)
).astype(int)

pressure["boundary_conceded"] = (
    (pressure["is_four"] == 1) |
    (pressure["is_six"] == 1)
).astype(int)

bowling = (
    pressure.groupby(["bowler_id", "bowler_name"])
    .agg(
        wickets=("bowler_wicket", "sum"),
        legal_balls=("legal_ball", "sum"),
        dot_balls=("dot_ball", "sum"),
        boundaries=("boundary_conceded", "sum"),
        matches=("match_id", "nunique")
    )
    .reset_index()
)

bowling = bowling[
    (bowling["legal_balls"] >= 50) &
    (bowling["matches"] >= 3)
].copy()

bowling["dot_percentage"] = (
    bowling["dot_balls"] / bowling["legal_balls"]
) * 100

bowling["wicket_rate"] = (
    bowling["wickets"] / bowling["legal_balls"]
) * 100

bowling["boundary_percentage"] = (
    bowling["boundaries"] / bowling["legal_balls"]
) * 100

bowling["wicket_score"] = bowling["wicket_rate"].rank(pct=True) * 100

bowling["dot_score"] = bowling["dot_percentage"].rank(pct=True) * 100

bowling["boundary_score"] = (
    (1 - bowling["boundary_percentage"].rank(pct=True)) * 100
)

bowling["reliability_score"] = (
    bowling["wicket_score"] * 0.40 +
    bowling["dot_score"] * 0.35 +
    bowling["boundary_score"] * 0.25
)

bowling = bowling.sort_values(
    "reliability_score", ascending=False
)

bowling["rank"] = range(1, len(bowling) + 1)

bowling.to_csv("improved_bowling_rankings.csv", index=False)

print("\nIMPROVED BOWLING MODEL COMPLETED")
print("--------------------------------")

print(
    bowling[
        [
            "rank",
            "bowler_name",
            "wickets",
            "legal_balls",
            "dot_percentage",
            "wicket_rate",
            "reliability_score"
        ]
    ].head(15).to_string(index=False)
)

print("\nFile generated: improved_bowling_rankings.csv")