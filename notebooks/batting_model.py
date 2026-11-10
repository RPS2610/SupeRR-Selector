import pandas as pd
import numpy as np
import os

DATA_PATH = "../results"
OUTPUT_PATH = "../results"

print("=" * 65)
print("SUPERR SELECTOR - BATTING PRESSURE MODEL")
print("=" * 65)

ball = pd.read_csv(
    os.path.join(DATA_PATH, "pressure_data.csv")
)

print("\nDataset Loaded Successfully")
print("Total Deliveries:", len(ball))

# Identify pressure and normal situations

ball["pressure_type"] = np.where(
    ball["pressure_level"].isin(["High", "Very High"]),
    "Pressure",
    "Normal"
)

# Identify legal deliveries for balls faced

if "is_wide" in ball.columns:
    legal_ball = ball["is_wide"].fillna(0) == 0
else:
    legal_ball = pd.Series(True, index=ball.index)

if "is_no_ball" in ball.columns:
    legal_ball = legal_ball & (
        ball["is_no_ball"].fillna(0) == 0
    )

ball["valid_ball"] = legal_ball.astype(int)

# Calculate batting statistics

batting = ball.groupby(
    ["striker_id", "striker_name", "pressure_type"]
).agg(
    runs=("runs", "sum"),
    balls=("valid_ball", "sum"),
    fours=("is_four", "sum"),
    sixes=("is_six", "sum")
).reset_index()

batting["strike_rate"] = np.where(
    batting["balls"] > 0,
    batting["runs"] / batting["balls"] * 100,
    0
)

# Separate normal and pressure performances

pressure = batting[
    batting["pressure_type"] == "Pressure"
].copy()

normal = batting[
    batting["pressure_type"] == "Normal"
].copy()

pressure = pressure.rename(columns={
    "runs": "pressure_runs",
    "balls": "pressure_balls",
    "fours": "pressure_fours",
    "sixes": "pressure_sixes",
    "strike_rate": "pressure_sr"
})

normal = normal.rename(columns={
    "runs": "normal_runs",
    "balls": "normal_balls",
    "strike_rate": "normal_sr"
})

# Combine both performances

result = pressure.merge(
    normal,
    on=["striker_id", "striker_name"],
    how="left"
)

result["normal_sr"] = result["normal_sr"].fillna(0)
result["normal_runs"] = result["normal_runs"].fillna(0)
result["normal_balls"] = result["normal_balls"].fillna(0)

# Calculate overall performance

result["overall_runs"] = (
    result["pressure_runs"] + result["normal_runs"]
)

result["overall_balls"] = (
    result["pressure_balls"] + result["normal_balls"]
)

result["overall_sr"] = np.where(
    result["overall_balls"] > 0,
    result["overall_runs"] / result["overall_balls"] * 100,
    0
)

# Calculate pressure performance difference

result["pressure_sr_difference"] = (
    result["pressure_sr"] - result["normal_sr"]
)

result["pressure_run_percentage"] = np.where(
    result["overall_runs"] > 0,
    result["pressure_runs"] / result["overall_runs"] * 100,
    0
)

result["boundary_runs"] = (
    result["pressure_fours"] * 4 +
    result["pressure_sixes"] * 6
)

result["boundary_percentage"] = np.where(
    result["pressure_runs"] > 0,
    result["boundary_runs"] / result["pressure_runs"] * 100,
    0
)

# Minimum sample size

eligible = result[
    (result["pressure_balls"] >= 30) &
    (result["overall_balls"] >= 100)
].copy()

# Initial pressure rating

eligible["pressure_rating"] = (
    0.50 * eligible["pressure_sr"] +
    0.30 * eligible["overall_sr"] +
    0.20 * eligible["pressure_sr_difference"]
)

# Sort players

eligible = eligible.sort_values(
    "pressure_rating",
    ascending=False
)

eligible["rank"] = range(1, len(eligible) + 1)

# Display Top 20

print("\nTOP 20 BATTERS UNDER PRESSURE")

columns = [
    "rank",
    "striker_name",
    "pressure_runs",
    "pressure_balls",
    "pressure_sr",
    "normal_sr",
    "pressure_sr_difference",
    "overall_sr",
    "pressure_rating"
]

print(
    eligible[columns].head(20).round(2).to_string(index=False)
)

# Save results

eligible.to_csv(
    os.path.join(OUTPUT_PATH, "batting_pressure_rankings.csv"),
    index=False
)

print("\nBATTER ANALYSIS COMPLETED")

print("\nFile generated:")
print("batting_pressure_rankings.csv")