import json
from pathlib import Path

from score_engine import calculate_total_runs, calculate_wickets, calculate_legal_balls

PROJECT_ROOT=Path(__file__).resolve().parents[1]
MATCH_FILE=PROJECT_ROOT / "data" / "raw" / "sample_match.json"

def main():
    with open(MATCH_FILE, 'r', encoding='utf-8') as file:
        Match=json.load(file)

    for inning in Match['innings']:
        Total_runs=calculate_total_runs(inning)
        Total_wickets=calculate_wickets(inning)
        legal_balls=calculate_legal_balls(inning)
        print(f"{inning['team']}: {Total_runs}/{Total_wickets}")
        print(f"{legal_balls} legal balls")


if __name__ == "__main__":
    main()