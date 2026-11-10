import pandas as pd
import numpy as np
import os

DATA_PATH = "../data"
RESULT_PATH = "../results"

os.makedirs(RESULT_PATH, exist_ok=True)

print("=" * 65)
print("SUPERR SELECTOR - DATA VALIDATION")
print("=" * 65)

ball = pd.read_csv(
    os.path.join(DATA_PATH, "ball_by_ball.csv")
)

print("\nDataset Loaded:", len(ball), "deliveries")

# 1. Validate extras

print("\nEXTRAS DISTRIBUTION")

print(
    ball["extras_type"]
    .value_counts(dropna=False)
)

# 2. Create legal delivery indicator

ball["is_wide_delivery"] = (
    ball["extras_type"] == "wide"
)

ball["is_noball_delivery"] = (
    ball["extras_type"] == "Overstep"
)

ball["legal_delivery"] = (
    ~ball["is_wide_delivery"] &
    ~ball["is_noball_delivery"]
)

# 3. Calculate batter balls faced

ball["batter_ball_faced"] = (
    ~ball["is_wide_delivery"]
).astype(int)

# 4. Identify wickets credited to bowlers

bowler_dismissals = [
    "Caught",
    "Bowled",
    "LBW",
    "Stump",
    "Hit Wicket"
]

ball["bowler_wicket"] = (
    ball["is_wicket"].fillna(False).astype(bool) &
    ball["dismissal_type"].isin(bowler_dismissals)
).astype(int)

# 5. Calculate bowler-conceded runs

ball["bowler_runs"] = (
    ball["runs"].fillna(0)
)

ball.loc[
    ball["extras_type"] == "wide",
    "bowler_runs"
] += 1

ball.loc[
    ball["extras_type"] == "Overstep",
    "bowler_runs"
] += 1

# 6. Generate validation summary

summary = pd.DataFrame({
    "Metric": [
        "Total Deliveries",
        "Wide Deliveries",
        "No Ball Deliveries",
        "Legal Deliveries",
        "Batter Balls Faced",
        "Total Dismissals",
        "Bowler Credited Wickets",
        "Run Outs",
        "Total Batter Runs",
        "Total Bowler Conceded Runs"
    ],

    "Value": [
        len(ball),
        ball["is_wide_delivery"].sum(),
        ball["is_noball_delivery"].sum(),
        ball["legal_delivery"].sum(),
        ball["batter_ball_faced"].sum(),
        ball["is_wicket"].sum(),
        ball["bowler_wicket"].sum(),
        (ball["dismissal_type"] == "RunOut").sum(),
        ball["runs"].sum(),
        ball["bowler_runs"].sum()
    ]
})

print("\nVALIDATION SUMMARY")

print(summary.to_string(index=False))

# 7. Save corrected delivery data

ball.to_csv(
    os.path.join(
        RESULT_PATH,
        "validated_ball_data.csv"
    ),
    index=False
)

summary.to_csv(
    os.path.join(
        RESULT_PATH,
        "data_validation_summary.csv"
    ),
    index=False
)

print("\nVALIDATION COMPLETED")

print("Generated Files:")
print("1. validated_ball_data.csv")
print("2. data_validation_summary.csv")