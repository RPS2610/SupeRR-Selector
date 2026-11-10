import pandas as pd
import os

DATA_PATH = "data"

files = {
    "ball_by_ball": "ball_by_ball.csv",
    "matches": "matches.csv",
    "playing_eleven": "playing_eleven.csv",
    "competitions": "competitions.csv",
    "teams": "teams.csv",
    "player_mapping": "competition_team_player_mapping.csv"
}

data = {}

for name, filename in files.items():

    path = os.path.join(DATA_PATH, filename)

    data[name] = pd.read_csv(path)

    print(f"\nDataset: {name}")
    print("Rows:", data[name].shape[0])
    print("Columns:", data[name].shape[1])
    print("Column Names:", list(data[name].columns))