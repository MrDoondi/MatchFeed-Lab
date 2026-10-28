import unittest
import json
from pathlib import Path
from src.score_engine import calculate_legal_balls,calculate_total_runs,calculate_wickets
from src.duplicate_experiment import process_event

class TestScoreEngine(unittest.TestCase):
    
    def test_calculate_total_runs(self):
        innings={
            "overs":[
                {
                    "deliveries":[
                        {"runs":{"total":4}},
                        {"runs":{"total":1}},
                    ]
                }
            ]
        }

        self.assertEqual(calculate_total_runs(innings),5)

    def test_calculate_wickets(self):
        innings = {
            "overs": [
                {
                    "deliveries": [
                        {"runs": {"total": 0}, "wickets": [{"kind": "bowled"}]},
                        {"runs": {"total": 1}},
                    ]
                }
            ]
        }

        self.assertEqual(calculate_wickets(innings), 1)

    def test_calculate_legal_balls(self):
        innings = {
            "overs": [
                {
                    "deliveries": [
                        {"runs": {"total": 0}},
                        {"runs": {"total": 1}, "extras": {"wides": 1}},
                        {"runs": {"total": 1}, "extras": {"noballs": 1}},
                        {"runs": {"total": 2}, "extras": {"legbyes": 2}},
                    ]
                }
            ]
        }

        self.assertEqual(calculate_legal_balls(innings), 2)

    def test_real_match_scores(self):
        PROJECT_ROOT=Path(__file__).resolve().parents[1]
        MATCH_FILE=PROJECT_ROOT / "data" / "raw" / "sample_match.json"

        with open(MATCH_FILE, "r", encoding='utf-8') as file:
            match=json.load(file)

        new_zeland, india =match["innings"]

        self.assertEqual(calculate_total_runs(new_zeland),180)
        self.assertEqual(calculate_wickets(new_zeland),5)
        self.assertEqual(calculate_legal_balls(new_zeland),120)
        self.assertEqual(calculate_total_runs(india),181)
        self.assertEqual(calculate_wickets(india),6)
        self.assertEqual(calculate_legal_balls(india),119)

    def test_duplicate_event_does_not_change_score_twice(self):
        score = 0
        processed_event_ids = {}
        event = {"delivery_id": "event-001", "runs": 4}

        score = process_event(score, event, processed_event_ids)
        score = process_event(score, event, processed_event_ids)

        self.assertEqual(score, 4)

    def test_different_events_both_change_score(self):
        score = 0
        processed_event_ids = {}

        event_1 = {"delivery_id": "event-001", "runs": 4}
        event_2 = {"delivery_id": "event-002", "runs": 2}

        score = process_event(score, event_1, processed_event_ids)
        score = process_event(score, event_2, processed_event_ids)

        self.assertEqual(score, 6)

    
    def test_conflicting_event_id_is_rejected(self):
        score = 0
        processed_events = {}

        original = {"delivery_id": "event-001", "runs": 4}
        conflicting = {"delivery_id": "event-001", "runs": 6}

        score = process_event(score, original, processed_events)

        with self.assertRaises(ValueError):
            process_event(score, conflicting, processed_events)

        self.assertEqual(score, 4)
        self.assertEqual(processed_events["event-001"], 4)

    def test_missing_total_runs_is_rejected(self):
        innings = {
            "overs": [
                {
                    "deliveries": [
                        {"runs": {}}
                    ]
                }
            ]
        }

        with self.assertRaisesRegex(
            ValueError, "total"
        ):
            calculate_total_runs(innings)

    def test_missing_runs_is_rejected(self):
        innings = {
            "overs": [{"deliveries": [{}]}]
        }

        with self.assertRaisesRegex(ValueError, "runs"):
            calculate_total_runs(innings)


    def test_runs_must_be_a_dictionary(self):
        innings = {
            "overs": [{"deliveries": [{"runs": None}]}]
        }

        with self.assertRaisesRegex(ValueError, "dictionary"):
            calculate_total_runs(innings)


    def test_string_total_is_rejected(self):
        innings = {
            "overs": [
                {"deliveries": [{"runs": {"total": "4"}}]}
            ]
        }

        with self.assertRaisesRegex(ValueError, "non-negative integer"):
            calculate_total_runs(innings)


    def test_float_total_is_rejected(self):
        innings = {
            "overs": [
                {"deliveries": [{"runs": {"total": 4.0}}]}
            ]
        }

        with self.assertRaisesRegex(ValueError, "non-negative integer"):
            calculate_total_runs(innings)


    def test_negative_total_is_rejected(self):
        innings = {
            "overs": [
                {"deliveries": [{"runs": {"total": -1}}]}
            ]
        }

        with self.assertRaisesRegex(ValueError, "non-negative integer"):
            calculate_total_runs(innings)


    def test_boolean_total_is_rejected(self):
        innings = {
            "overs": [
                {"deliveries": [{"runs": {"total": True}}]}
            ]
        }

        with self.assertRaisesRegex(ValueError, "non-negative integer"):
            calculate_total_runs(innings)


    def test_zero_total_is_accepted(self):
        innings = {
            "overs": [
                {"deliveries": [{"runs": {"total": 0}}]}
            ]
        }

        self.assertEqual(calculate_total_runs(innings), 0)

    

if __name__ == "__main__":
    unittest.main()