import pandas as pd
import numpy as np
import os

DATA_PATH = "../results"
OUTPUT_PATH = "../results"

print("=" * 65)
print("SUPERR SELECTOR - BOWLING PRESSURE MODEL")
print("=" * 65)

ball = pd.read_csv(
    os.path.join(DATA_PATH, "pressure_data.csv")
)

print("\nDataset Loaded Successfully")
print("Total Deliveries:", len(ball))

# Classify pressure and normal situations

ball["pressure_type"] = np.where(
    ball["pressure_level"].isin(["High", "Very High"]),
    "Pressure",
    "Normal"
)

# Identify legal deliveries

ball["legal_ball"] = ~ball["extras_type"].isin(
    ["wide", "Overstep"]
)

ball["legal_ball"] = (
    ball["legal_ball"].fillna(True).astype(int)
)

# Identify wickets credited to bowlers

bowler_dismissals = [
    "Bowled",
    "Caught",
    "LBW",
    "Stump",
    "Hit Wicket"
]

ball["bowler_wicket"] = (
    ball["is_wicket"].astype(bool) &
    ball["dismissal_type"].isin(bowler_dismissals)
).astype(int)

# Calculate bowling statistics

bowling = ball.groupby(
    ["bowler_id", "bowler_name", "pressure_type"]
).agg(
    runs_conceded=("runs", "sum"),
    deliveries=("legal_ball", "sum"),
    wickets=("bowler_wicket", "sum"),
    dot_balls=("runs", lambda x: (x == 0).sum())
).reset_index()

# Calculate bowling metrics

bowling["economy"] = np.where(
    bowling["deliveries"] > 0,
    bowling["runs_conceded"] * 6 /
    bowling["deliveries"],
    0
)

bowling["bowling_average"] = np.where(
    bowling["wickets"] > 0,
    bowling["runs_conceded"] /
    bowling["wickets"],
    np.nan
)

bowling["bowling_strike_rate"] = np.where(
    bowling["wickets"] > 0,
    bowling["deliveries"] /
    bowling["wickets"],
    np.nan
)

bowling["dot_ball_percentage"] = np.where(
    bowling["deliveries"] > 0,
    bowling["dot_balls"] /
    bowling["deliveries"] * 100,
    0
)

# Separate pressure and normal performances

pressure = bowling[
    bowling["pressure_type"] == "Pressure"
].copy()

normal = bowling[
    bowling["pressure_type"] == "Normal"
].copy()

pressure = pressure.rename(columns={
    "runs_conceded": "pressure_runs",
    "deliveries": "pressure_deliveries",
    "wickets": "pressure_wickets",
    "economy": "pressure_economy",
    "bowling_average": "pressure_average",
    "bowling_strike_rate": "pressure_strike_rate",
    "dot_ball_percentage": "pressure_dot_percentage"
})

normal = normal.rename(columns={
    "runs_conceded": "normal_runs",
    "deliveries": "normal_deliveries",
    "wickets": "normal_wickets",
    "economy": "normal_economy",
    "bowling_average": "normal_average",
    "bowling_strike_rate": "normal_strike_rate",
    "dot_ball_percentage": "normal_dot_percentage"
})

# Combine pressure and normal statistics

result = pressure.merge(
    normal,
    on=["bowler_id", "bowler_name"],
    how="left"
)

fill_columns = [
    "normal_runs",
    "normal_deliveries",
    "normal_wickets",
    "normal_economy",
    "normal_dot_percentage"
]

result[fill_columns] = result[fill_columns].fillna(0)

# Calculate overall statistics

result["overall_runs"] = (
    result["pressure_runs"] +
    result["normal_runs"]
)

result["overall_deliveries"] = (
    result["pressure_deliveries"] +
    result["normal_deliveries"]
)

result["overall_wickets"] = (
    result["pressure_wickets"] +
    result["normal_wickets"]
)

result["overall_economy"] = np.where(
    result["overall_deliveries"] > 0,
    result["overall_runs"] * 6 /
    result["overall_deliveries"],
    0
)

# Calculate pressure differences

result["economy_difference"] = (
    result["normal_economy"] -
    result["pressure_economy"]
)

result["dot_difference"] = (
    result["pressure_dot_percentage"] -
    result["normal_dot_percentage"]
)

# Minimum sample size

eligible = result[
    (result["pressure_deliveries"] >= 30) &
    (result["overall_deliveries"] >= 100)
].copy()

# Initial bowling pressure rating

eligible["pressure_rating"] = (
    0.40 * eligible["pressure_dot_percentage"] +
    0.35 * (100 - eligible["pressure_economy"] * 6) +
    0.25 * eligible["pressure_wickets"] /
    eligible["pressure_deliveries"] * 600
)

# Rank bowlers

eligible = eligible.sort_values(
    "pressure_rating",
    ascending=False
)

eligible["rank"] = range(
    1, len(eligible) + 1
)

# Display Top 20 bowlers

print("\nTOP 20 BOWLERS UNDER PRESSURE")

columns = [
    "rank",
    "bowler_name",
    "pressure_wickets",
    "pressure_deliveries",
    "pressure_economy",
    "normal_economy",
    "economy_difference",
    "pressure_dot_percentage",
    "pressure_rating"
]

print(
    eligible[columns]
    .head(20)
    .round(2)
    .to_string(index=False)
)

# Save results

eligible.to_csv(
    os.path.join(
        OUTPUT_PATH,
        "bowling_pressure_rankings.csv"
    ),
    index=False
)

print("\nBOWLING ANALYSIS COMPLETED")

print("\nFile generated:")
print("bowling_pressure_rankings.csv")