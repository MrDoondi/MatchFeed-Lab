
import unittest

from src.ordered_replay import replay_events


class TestOrderedReplay(unittest.TestCase):
    def test_replays_out_of_order_arrivals_correctly(self):
        events = [
            {"sequence": 2, "delivery_id": "B", "runs": 4},
            {"sequence": 1, "delivery_id": "A", "runs": 2},
        ]

        self.assertEqual(replay_events(events), 6)

    def test_detects_missing_sequence(self):
        events = [
            {"sequence": 1, "delivery_id": "A", "runs": 2},
            {"sequence": 3, "delivery_id": "C", "runs": 4},
        ]

        with self.assertRaisesRegex(ValueError, "Missing event"):
            replay_events(events)

    def test_detects_duplicate_sequence(self):
        events = [
            {"sequence": 1, "delivery_id": "A", "runs": 2},
            {"sequence": 2, "delivery_id": "B", "runs": 4},
            {"sequence": 2, "delivery_id": "C", "runs": 1},
        ]

        with self.assertRaisesRegex(
            ValueError, "Duplicate sequence number"
        ):
            replay_events(events)


if __name__ == "__main__":
    unittest.main()
