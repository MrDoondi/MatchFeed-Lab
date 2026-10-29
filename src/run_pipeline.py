import json
from pathlib import Path

from src.delivery_adapter import build_delivery_events
from src.innings_replay import replay_innings
from src.score_engine import (
    calculate_total_runs,
    calculate_wickets,
    calculate_legal_balls,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MATCH_FILE = PROJECT_ROOT / "data" / "raw" / "sample_match.json"


def main():
    with open(MATCH_FILE, "r", encoding="utf-8") as file:
        match = json.load(file)

    print("MATCHFEED LAB — BATCH REPLAY VERIFICATION")
    print("=" * 45)

    for innings_number, innings in enumerate(
        match["innings"], start=1
    ):
        events = build_delivery_events(innings, innings_number)

        result = replay_innings(events, innings["team"])

        baseline = {
            "runs": calculate_total_runs(innings),
            "wickets": calculate_wickets(innings),
            "legal_balls": calculate_legal_balls(innings),
        }

        replay_totals = {
            "runs": result["runs"],
            "wickets": result["wickets"],
            "legal_balls": result["legal_balls"],
        }

        verified = replay_totals == baseline

        print(f"\nInnings {innings_number}: {result['team']}")
        print(f"Score: {result['runs']}/{result['wickets']}")
        print(f"Legal balls: {result['legal_balls']}")
        print(f"Extra runs: {result['extra_runs']}")
        print(
            f"Delivery records processed: "
            f"{result['deliveries_processed']}"
        )
        print(
            f"Baseline verification: "
            f"{'PASS' if verified else 'FAIL'}"
        )

        if not verified:
            print(f"Replay totals: {replay_totals}")
            print(f"Baseline totals: {baseline}")
            raise AssertionError(
                f"Replay verification failed for {result['team']}"
            )

    print("\nAll innings verified successfully.")


if __name__ == "__main__":
    main()