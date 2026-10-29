
import json
from pathlib import Path

from src.buffered_replay import BufferedReplay
from src.delivery_adapter import build_delivery_events
from src.score_engine import (
    calculate_total_runs,
    calculate_wickets,
    calculate_legal_balls,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MATCH_FILE = PROJECT_ROOT / "data" / "raw" / "sample_match.json"


def stream_events_with_delays(replay, events):
    """Simulate delayed arrivals while preserving every event."""
    index = 0

    while index < len(events):
        # Send events in pairs, deliberately reversing their arrival order.
        batch = events[index:index + 2]

        for event in reversed(batch):
            replay.receive(event)

        index += 2


def main():
    with open(MATCH_FILE, "r", encoding="utf-8") as file:
        match = json.load(file)

    print("MATCHFEED LAB — STREAMING REPLAY VERIFICATION")
    print("=" * 48)

    for innings_number, innings in enumerate(
        match["innings"], start=1
    ):
        events = build_delivery_events(innings, innings_number)

        # Add the delivery ID expected by BufferedReplay.
        streaming_events = [
            {
                **event,
                "delivery_id": f"innings-{innings_number}-delivery-{event['sequence']}",
            }
            for event in events
        ]

        replay = BufferedReplay()
        stream_events_with_delays(replay, streaming_events)

        baseline = {
            "runs": calculate_total_runs(innings),
            "wickets": calculate_wickets(innings),
            "legal_balls": calculate_legal_balls(innings),
        }

        replay_totals = {
            "runs": replay.score,
            "wickets": replay.total_wickets,
            "legal_balls": replay.legal_balls,
        }

        expected_extra_runs = sum(
            delivery["runs"]["extras"]
            for over in innings["overs"]
            for delivery in over["deliveries"]
        )

        verified = (
            replay_totals == baseline
            and replay.extra_runs == expected_extra_runs
            and replay.get_status()["status"] == "caught_up"
        )

        print(f"\nInnings {innings_number}: {innings['team']}")
        print(f"Score: {replay.score}/{replay.total_wickets}")
        print(f"Legal balls: {replay.legal_balls}")
        print(f"Extra runs: {replay.extra_runs}")
        print(f"Events processed: {len(replay.processed_events)}")
        print(f"Events buffered at end: {len(replay.buffer)}")
        print(f"Verification: {'PASS' if verified else 'FAIL'}")

        if not verified:
            print(f"Expected totals: {baseline}")
            print(f"Streaming totals: {replay_totals}")
            raise AssertionError(
                f"Streaming verification failed for {innings['team']}"
            )

    print("\nAll innings verified successfully.")


if __name__ == "__main__":
    main()
