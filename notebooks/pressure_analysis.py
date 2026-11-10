import pandas as pd
import os

DATA_PATH = "../data"
RESULT_PATH = "../results"

os.makedirs(RESULT_PATH, exist_ok=True)

print("=" * 60)
print("SUPERR SELECTOR - PRESSURE ANALYSIS")
print("=" * 60)

ball = pd.read_csv(
    os.path.join(DATA_PATH, "ball_by_ball.csv")
)

print("\nDataset Loaded Successfully")
print("Total Deliveries:", len(ball))

ball = ball.sort_values(
    ["match_id", "innings", "overid", "over_ball_num"]
).copy()

# Step 1: Identify innings stage

def get_innings_stage(over):

    if over <= 6:
        return "Powerplay"

    elif over <= 15:
        return "Middle Overs"

    else:
        return "Death Overs"


ball["innings_stage"] = ball["overid"].apply(
    get_innings_stage
)

# Step 2: Calculate wickets lost before each delivery

ball["wickets_lost"] = (
    ball.groupby(["match_id", "innings"])["is_wicket"]
    .transform(lambda x: x.astype(int).cumsum().shift(fill_value=0))
)

ball["wickets_remaining"] = (
    10 - ball["wickets_lost"]
)

# Step 3: Identify pressure levels

def identify_pressure(row):

    if row["wickets_remaining"] <= 2:
        return "Very High"

    elif (
        row["innings_stage"] == "Death Overs"
        or row["wickets_remaining"] <= 5
    ):
        return "High"

    elif (
        row["innings_stage"] == "Middle Overs"
        or row["wickets_remaining"] <= 7
    ):
        return "Medium"

    else:
        return "Low"


ball["pressure_level"] = ball.apply(
    identify_pressure,
    axis=1
)

# Step 4: Generate pressure summary

pressure_summary = (
    ball.groupby("pressure_level")
    .agg(
        total_deliveries=("match_id", "count"),
        total_runs=("runs", "sum"),
        total_wickets=("is_wicket", "sum")
    )
    .reset_index()
)

print("\nPRESSURE DISTRIBUTION")
print(pressure_summary.to_string(index=False))

# Step 5: Analyse pressure by innings stage

stage_summary = (
    ball.groupby("innings_stage")
    .agg(
        total_deliveries=("match_id", "count"),
        total_runs=("runs", "sum"),
        total_wickets=("is_wicket", "sum")
    )
    .reset_index()
)

print("\nINNINGS STAGE ANALYSIS")
print(stage_summary.to_string(index=False))

# Step 6: Save results

pressure_summary.to_csv(
    os.path.join(RESULT_PATH, "pressure_summary.csv"),
    index=False
)

stage_summary.to_csv(
    os.path.join(RESULT_PATH, "stage_summary.csv"),
    index=False
)

ball.to_csv(
    os.path.join(RESULT_PATH, "pressure_data.csv"),
    index=False
)

print("\n" + "=" * 60)
print("PRESSURE ANALYSIS COMPLETED")
print("=" * 60)

print("\nFiles saved inside results folder:")
print("1. pressure_summary.csv")
print("2. stage_summary.csv")
print("3. pressure_data.csv")