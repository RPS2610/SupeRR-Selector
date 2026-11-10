import pandas as pd
import numpy as np
import os

DATA_PATH = "../data/ball_by_ball.csv"
OUTPUT_PATH = "advanced_pressure_analysis.csv"

df = pd.read_csv(DATA_PATH)

required_columns = [
    "match_id", "innings", "overid",
    "striker_id", "striker_name",
    "bowler_id", "bowler_name",
    "is_wicket"
]

missing = [col for col in required_columns if col not in df.columns]

if missing:
    raise ValueError(f"Missing columns: {missing}")

df = df.copy()

df["is_wicket"] = pd.to_numeric(
    df["is_wicket"], errors="coerce"
).fillna(0)

df["overid"] = pd.to_numeric(
    df["overid"], errors="coerce"
).fillna(0)

df = df.sort_values(
    ["match_id", "innings", "overid"]
).reset_index(drop=True)

group_columns = ["match_id", "innings"]

df["wickets_before"] = (
    df.groupby(group_columns)["is_wicket"]
    .cumsum() - df["is_wicket"]
)

df["wickets_remaining"] = (10 - df["wickets_before"]).clip(lower=0)

df["match_stage"] = np.select(
    [
        df["overid"] <= 6,
        df["overid"] <= 15
    ],
    [
        "Powerplay",
        "Middle Overs"
    ],
    default="Death Overs"
)

stage_score = {
    "Powerplay": 1,
    "Middle Overs": 2,
    "Death Overs": 3
}

df["stage_score"] = df["match_stage"].map(stage_score)

df["wicket_pressure"] = np.select(
    [
        df["wickets_remaining"] <= 2,
        df["wickets_remaining"] <= 4,
        df["wickets_remaining"] <= 6,
        df["wickets_remaining"] <= 8
    ],
    [4, 3, 2, 1],
    default=0
)

df["pressure_score"] = (
    df["stage_score"] + df["wicket_pressure"]
)

df["pressure_level"] = np.select(
    [
        df["pressure_score"] >= 6,
        df["pressure_score"] >= 4,
        df["pressure_score"] >= 2
    ],
    [
        "Very High",
        "High",
        "Medium"
    ],
    default="Low"
)

df.to_csv(OUTPUT_PATH, index=False)

summary = (
    df.groupby("pressure_level")
    .agg(
        deliveries=("match_id", "count"),
        average_wickets_lost=("wickets_before", "mean")
    )
    .reset_index()
)

summary.to_csv("pressure_level_summary.csv", index=False)

print("\nADVANCED PRESSURE ANALYSIS COMPLETED")
print("------------------------------------")
print(summary.to_string(index=False))

print("\nFiles generated:")
print("1. advanced_pressure_analysis.csv")
print("2. pressure_level_summary.csv")