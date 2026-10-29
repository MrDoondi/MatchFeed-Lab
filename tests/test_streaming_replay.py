
import contextlib
import io
import json
import unittest
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


class TestStreamingReplayIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(MATCH_FILE, "r", encoding="utf-8") as file:
            cls.match = json.load(file)

    def test_streaming_replay_matches_both_real_innings(self):
        expected_scores = [
            {"runs": 180, "wickets": 5, "legal_balls": 120},
            {"runs": 181, "wickets": 6, "legal_balls": 119},
        ]

        for innings_number, innings in enumerate(
            self.match["innings"], start=1
        ):
            with self.subTest(innings=innings_number):
                events = build_delivery_events(
                    innings, innings_number
                )

                streaming_events = [
                    {
                        **event,
                        "delivery_id": (
                            f"innings-{innings_number}-"
                            f"delivery-{event['sequence']}"
                        ),
                    }
                    for event in events
                ]

                replay = BufferedReplay()

                # Reverse each pair to simulate out-of-order arrival.
                with contextlib.redirect_stdout(io.StringIO()):
                    for index in range(0, len(streaming_events), 2):
                        batch = streaming_events[index:index + 2]

                        for event in reversed(batch):
                            replay.receive(event)

                baseline = {
                    "runs": calculate_total_runs(innings),
                    "wickets": calculate_wickets(innings),
                    "legal_balls": calculate_legal_balls(innings),
                }

                self.assertEqual(baseline, expected_scores[innings_number - 1])
                self.assertEqual(replay.score, baseline["runs"])
                self.assertEqual(replay.total_wickets, baseline["wickets"])
                self.assertEqual(replay.legal_balls, baseline["legal_balls"])

                expected_extras = sum(
                    delivery["runs"]["extras"]
                    for over in innings["overs"]
                    for delivery in over["deliveries"]
                )

                self.assertEqual(replay.extra_runs, expected_extras)
                self.assertEqual(
                    len(replay.processed_events), len(streaming_events)
                )
                self.assertEqual(replay.buffer, {})
                self.assertEqual(
                    replay.get_status()["status"], "caught_up"
                )

    def test_streaming_replay_recovers_when_missing_event_arrives(self):
        event_1 = {
            "sequence": 1,
            "delivery_id": "delivery-1",
            "delivery": {
                "runs": {"batter": 1, "extras": 0, "total": 1}
            },
        }
        event_2 = {
            "sequence": 2,
            "delivery_id": "delivery-2",
            "delivery": {
                "runs": {"batter": 4, "extras": 0, "total": 4}
            },
        }

        replay = BufferedReplay()

        with contextlib.redirect_stdout(io.StringIO()):
            replay.receive(event_2)

        self.assertEqual(replay.score, 0)
        self.assertEqual(
            replay.get_status()["status"],
            "waiting_for_missing_event",
        )

        with contextlib.redirect_stdout(io.StringIO()):
            replay.receive(event_1)

        self.assertEqual(replay.score, 5)
        self.assertEqual(len(replay.processed_events), 2)
        self.assertEqual(replay.buffer, {})
        self.assertEqual(replay.get_status()["status"], "caught_up")


if __name__ == "__main__":
    unittest.main()
