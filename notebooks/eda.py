import pandas as pd
import os

DATA_PATH = "../data"
RESULT_PATH = "../results"

os.makedirs(RESULT_PATH, exist_ok=True)

files = {
    "ball_by_ball": "ball_by_ball.csv",
    "matches": "matches.csv",
    "playing_eleven": "playing_eleven.csv",
    "competitions": "competitions.csv",
    "teams": "teams.csv",
    "player_mapping": "competition_team_player_mapping.csv"
}

data = {}

print("=" * 60)
print("SUPERR SELECTOR SEASON 2 - DATA ANALYSIS")
print("=" * 60)

for name, filename in files.items():

    path = os.path.join(DATA_PATH, filename)

    data[name] = pd.read_csv(path)

    print(f"\nDataset: {name}")
    print("Total Rows:", data[name].shape[0])
    print("Total Columns:", data[name].shape[1])
    print("Columns:", list(data[name].columns))

    print("Duplicate Rows:", data[name].duplicated().sum())

    print("\nMissing Values:")
    print(data[name].isnull().sum())


ball = data["ball_by_ball"]
matches = data["matches"]
competitions = data["competitions"]
players = data["player_mapping"]

print("\n" + "=" * 60)
print("GENERAL DATASET ANALYSIS")
print("=" * 60)

print("Total Deliveries:", len(ball))

print("Unique Matches:", ball["match_id"].nunique())

print("Unique Batters:", ball["striker_id"].nunique())

print("Unique Bowlers:", ball["bowler_id"].nunique())

print("Unique Players:", players["player_id"].nunique())

print("Total Competitions:", competitions["comp_id"].nunique())

print("\n" + "=" * 60)
print("COMPETITION ANALYSIS")
print("=" * 60)

competition_data = matches.merge(
    competitions,
    on="comp_id",
    how="left"
)

print(competition_data["match_format"].value_counts(dropna=False))

print("\nSeason-wise Matches:")

season_analysis = competition_data.groupby(
    ["match_format", "season"]
).size().reset_index(name="total_matches")

print(season_analysis.to_string(index=False))

season_analysis.to_csv(
    os.path.join(RESULT_PATH, "season_analysis.csv"),
    index=False
)

print("\n" + "=" * 60)
print("PLAYER ANALYSIS")
print("=" * 60)

batting_stats = ball.groupby(
    ["striker_id", "striker_name"]
).agg(
    total_runs=("runs", "sum"),
    balls_faced=("innings_ball_num", "count"),
    fours=("is_four", "sum"),
    sixes=("is_six", "sum")
).reset_index()

bowling_stats = ball.groupby(
    ["bowler_id", "bowler_name"]
).agg(
    deliveries=("match_id", "count"),
    wickets=("is_wicket", "sum")
).reset_index()

print("\nTop 10 Run Scorers:")
print(batting_stats.sort_values(
    "total_runs", ascending=False
).head(10).to_string(index=False))

print("\nTop 10 Bowlers by Wickets:")
print(bowling_stats.sort_values(
    "wickets", ascending=False
).head(10).to_string(index=False))

batting_stats.to_csv(
    os.path.join(RESULT_PATH, "batting_overview.csv"),
    index=False
)

bowling_stats.to_csv(
    os.path.join(RESULT_PATH, "bowling_overview.csv"),
    index=False
)

print("\n" + "=" * 60)
print("EDA COMPLETED SUCCESSFULLY")
print("=" * 60)

print("Reports saved inside the results folder.")