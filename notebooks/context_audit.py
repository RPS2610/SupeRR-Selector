import pandas as pd
import os

DATA_PATH = "../data"
RESULT_PATH = "../results"

os.makedirs(RESULT_PATH, exist_ok=True)

print("=" * 65)
print("SUPERR SELECTOR - MATCH CONTEXT AUDIT")
print("=" * 65)

ball = pd.read_csv(
    os.path.join(DATA_PATH, "ball_by_ball.csv")
)

matches = pd.read_csv(
    os.path.join(DATA_PATH, "matches.csv")
)

# 1. Inspect delivery data

print("\n1. DELIVERY DATA")

columns = [
    "match_id",
    "innings",
    "overid",
    "over_ball_num",
    "runs",
    "extras_type",
    "extras1_runs",
    "extras_2_runs",
    "is_wicket"
]

print(ball[columns].head(15).to_string(index=False))

# 2. Inspect extras categories

print("\n2. EXTRAS DISTRIBUTION")

print(
    ball["extras_type"]
    .value_counts(dropna=False)
)

# 3. Inspect innings

print("\n3. INNINGS DISTRIBUTION")

print(
    ball["innings"].value_counts()
)

# 4. Inspect match target information

print("\n4. MATCH TARGET INFORMATION")

target_columns = [
    "match_id",
    "comp_id",
    "first_inn_revised_overs",
    "second_inn_revised_overs",
    "revised_target",
    "win_team_id",
    "result"
]

print(
    matches[target_columns].head(15).to_string(index=False)
)

# 5. Check innings-level data

innings_summary = ball.groupby(
    ["match_id", "innings"]
).agg(
    deliveries=("match_id", "size"),
    batter_runs=("runs", "sum"),
    wickets=("is_wicket", "sum"),
    last_over=("overid", "max")
).reset_index()

print("\n5. INNINGS SUMMARY")

print(
    innings_summary.head(20).to_string(index=False)
)

# 6. Check matches with revised targets

print("\n6. REVISED TARGET ANALYSIS")

print(
    "Matches with revised targets:",
    matches["revised_target"].notna().sum()
)

print(
    "Matches with revised overs:",
    matches["second_inn_revised_overs"].notna().sum()
)

# 7. Save reports

innings_summary.to_csv(
    os.path.join(
        RESULT_PATH,
        "innings_context_audit.csv"
    ),
    index=False
)

print("\n" + "=" * 65)
print("CONTEXT AUDIT COMPLETED")
print("=" * 65)

print("\nGenerated file:")
print("innings_context_audit.csv")
