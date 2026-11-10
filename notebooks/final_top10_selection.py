import pandas as pd

batting = pd.read_csv("improved_batting_rankings.csv")
bowling = pd.read_csv("improved_bowling_rankings.csv")

top_batters = batting.head(10).copy()
top_bowlers = bowling.head(10).copy()

top_batters["category"] = "Batter"
top_bowlers["category"] = "Bowler"

top_batters = top_batters.rename(columns={
    "striker_name": "player_name"
})

top_bowlers = top_bowlers.rename(columns={
    "bowler_name": "player_name"
})

top_batters["final_rank"] = range(1, len(top_batters) + 1)
top_bowlers["final_rank"] = range(1, len(top_bowlers) + 1)

batting_output = top_batters[
    ["final_rank", "player_name", "reliability_score", "category"]
]

bowling_output = top_bowlers[
    ["final_rank", "player_name", "reliability_score", "category"]
]

final_list = pd.concat(
    [batting_output, bowling_output],
    ignore_index=True
)

final_list.to_csv("final_top10_shortlist.csv", index=False)

print("\nFINAL TOP 10 SHORTLIST")
print("=" * 45)

print("\nTOP 10 BATTERS")
print(batting_output.to_string(index=False))

print("\nTOP 10 BOWLERS")
print(bowling_output.to_string(index=False))

print("\nFile generated: final_top10_shortlist.csv")