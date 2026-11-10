import pandas as pd

files = {
    "Batting": "improved_batting_rankings.csv",
    "Bowling": "improved_bowling_rankings.csv"
}

for category, filename in files.items():

    print(f"\n{'=' * 45}")
    print(f"{category.upper()} RANKING VALIDATION")
    print("=" * 45)

    df = pd.read_csv(filename)

    print("Total players:", len(df))
    print("Duplicate player IDs:", df.iloc[:, 0].duplicated().sum())
    print("Missing values:", df.isnull().sum().sum())

    if "reliability_score" in df.columns:
        print(
            "Score range:",
            round(df["reliability_score"].min(), 2),
            "to",
            round(df["reliability_score"].max(), 2)
        )

    print("\nTop 10 Players:")

    print(
        df.head(10).to_string(index=False)
    )

    if len(df) < 10:
        print("\nWARNING: Fewer than 10 eligible players.")

print("\nRANKING VALIDATION COMPLETED")