import pandas as pd
import numpy as np
import os

RESULT_PATH = "../results"

print("=" * 65)
print("SUPERR SELECTOR - MODEL VALIDATION")
print("=" * 65)

# Load existing rankings

batting = pd.read_csv(
    os.path.join(
        RESULT_PATH,
        "batting_pressure_rankings.csv"
    )
)

bowling = pd.read_csv(
    os.path.join(
        RESULT_PATH,
        "bowling_pressure_rankings.csv"
    )
)

# BATTER VALIDATION

print("\n1. BATTING MODEL VALIDATION")

print("Total eligible batters:", len(batting))

print(
    "Minimum pressure balls:",
    batting["pressure_balls"].min()
)

print(
    "Maximum pressure balls:",
    batting["pressure_balls"].max()
)

print(
    "Average pressure strike rate:",
    round(batting["pressure_sr"].mean(), 2)
)

print("\nTop 10 Batters:")

print(
    batting[
        [
            "rank",
            "striker_name",
            "pressure_balls",
            "pressure_sr",
            "normal_sr",
            "pressure_rating"
        ]
    ].head(10).round(2).to_string(index=False)
)

# Check missing values

print("\nMissing batting values:")

print(
    batting.isnull().sum()
)

# BOWLER VALIDATION

print("\n2. BOWLING MODEL VALIDATION")

print("Total eligible bowlers:", len(bowling))

print(
    "Minimum pressure deliveries:",
    bowling["pressure_deliveries"].min()
)

print(
    "Maximum pressure deliveries:",
    bowling["pressure_deliveries"].max()
)

print(
    "Average pressure economy:",
    round(bowling["pressure_economy"].mean(), 2)
)

print("\nTop 10 Bowlers:")

print(
    bowling[
        [
            "rank",
            "bowler_name",
            "pressure_deliveries",
            "pressure_wickets",
            "pressure_economy",
            "pressure_rating"
        ]
    ].head(10).round(2).to_string(index=False)
)

print("\nMissing bowling values:")

print(
    bowling.isnull().sum()
)

# Extreme-value checks

print("\n3. EXTREME VALUE CHECKS")

print(
    "Batters with pressure SR above 250:",
    (batting["pressure_sr"] > 250).sum()
)

print(
    "Bowlers with pressure economy above 15:",
    (bowling["pressure_economy"] > 15).sum()
)

print(
    "Bowlers with zero pressure wickets:",
    (bowling["pressure_wickets"] == 0).sum()
)

# Save validation summary

summary = pd.DataFrame({
    "Category": ["Batters", "Bowlers"],
    "Eligible Players": [
        len(batting),
        len(bowling)
    ],
    "Minimum Sample": [
        batting["pressure_balls"].min(),
        bowling["pressure_deliveries"].min()
    ],
    "Maximum Sample": [
        batting["pressure_balls"].max(),
        bowling["pressure_deliveries"].max()
    ]
})

summary.to_csv(
    os.path.join(
        RESULT_PATH,
        "model_validation_summary.csv"
    ),
    index=False
)

print("\n" + "=" * 65)
print("VALIDATION CHECK COMPLETED")
print("=" * 65)