import json
import unittest
from pathlib import Path

from src.delivery_adapter import build_delivery_events
from src.innings_replay import replay_innings


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MATCH_FILE = PROJECT_ROOT / "data" / "raw" / "sample_match.json"


class TestPipeline(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open(MATCH_FILE, "r", encoding="utf-8") as file:
            cls.match = json.load(file)

    def test_events_have_contiguous_sequences(self):
        innings = self.match["innings"][0]
        events = build_delivery_events(innings, 1)

        sequences = [event["sequence"] for event in events]

        self.assertEqual(
            sequences,
            list(range(1, len(events) + 1)),
        )

    def test_original_delivery_is_preserved(self):
        innings = self.match["innings"][0]
        events = build_delivery_events(innings, 1)

        self.assertEqual(
            events[0]["delivery"],
            innings["overs"][0]["deliveries"][0],
        )

    def test_replay_matches_known_innings_totals(self):
        expected = [
            {
                "team": "New Zealand",
                "runs": 180,
                "wickets": 5,
                "legal_balls": 120,
            },
            {
                "team": "India",
                "runs": 181,
                "wickets": 6,
                "legal_balls": 119,
            },
        ]

        for number, innings in enumerate(
            self.match["innings"], start=1
        ):
            with self.subTest(team=innings["team"]):
                events = build_delivery_events(innings, number)
                result = replay_innings(events, innings["team"])

                for key, expected_value in expected[number - 1].items():
                    self.assertEqual(result[key], expected_value)

    def test_extra_runs_are_calculated(self):
        innings = self.match["innings"][0]
        events = build_delivery_events(innings, 1)

        result = replay_innings(events, innings["team"])

        expected_extra_runs = sum(
            delivery["runs"]["extras"]
            for over in innings["overs"]
            for delivery in over["deliveries"]
        )

        self.assertEqual(result["extra_runs"], expected_extra_runs)

    def test_wides_and_no_balls_are_not_legal_balls(self):
        events = [
            {
                "sequence": 1,
                "delivery": {
                    "runs": {"batter": 0, "extras": 1, "total": 1},
                    "extras": {"wides": 1},
                },
            },
            {
                "sequence": 2,
                "delivery": {
                    "runs": {"batter": 0, "extras": 1, "total": 1},
                    "extras": {"noballs": 1},
                },
            },
            {
                "sequence": 3,
                "delivery": {
                    "runs": {"batter": 1, "extras": 0, "total": 1},
                },
            },
        ]

        result = replay_innings(events, "Test Team")

        self.assertEqual(result["runs"], 3)
        self.assertEqual(result["extra_runs"], 2)
        self.assertEqual(result["legal_balls"], 1)
        self.assertEqual(result["deliveries_processed"], 3)

    def test_missing_sequence_is_rejected(self):
        events = [
            {
                "sequence": 1,
                "delivery": {"runs": {"total": 2, "extras": 0}},
            },
            {
                "sequence": 3,
                "delivery": {"runs": {"total": 4, "extras": 0}},
            },
        ]

        with self.assertRaisesRegex(
            ValueError, "Expected sequence 2"
        ):
            replay_innings(events, "Test Team")
    
    def test_empty_innings_returns_zero_totals(self):
        result = replay_innings([], "Test Team")

        self.assertEqual(result["team"], "Test Team")
        self.assertEqual(result["runs"], 0)
        self.assertEqual(result["wickets"], 0)
        self.assertEqual(result["legal_balls"], 0)
        self.assertEqual(result["deliveries_processed"], 0)
        self.assertEqual(result["extra_runs"], 0)

    def test_negative_sequence_is_rejected(self):
        events = [
            {
                "sequence": -1,
                "delivery": {
                    "runs": {"total": 2, "extras": 0}
                },
            }
        ]

        with self.assertRaisesRegex(ValueError, "Expected sequence 1"):
            replay_innings(events, "Test Team")

    def test_duplicate_sequence_is_rejected(self):
        delivery = {"runs": {"total": 1, "extras": 0}}
        events = [
            {"sequence": 1, "delivery": delivery},
            {"sequence": 1, "delivery": delivery},
        ]

        with self.assertRaisesRegex(ValueError, "Expected sequence 2"):
            replay_innings(events, "Test Team")

    def test_missing_runs_field_is_rejected(self):
        events = [
            {
                "sequence": 1,
                "delivery": {},
            }
        ]

        with self.assertRaises(KeyError):
            replay_innings(events, "Test Team")


if __name__ == "__main__":
    unittest.main()