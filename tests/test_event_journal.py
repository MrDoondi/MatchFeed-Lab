
import json
import tempfile
import unittest
from pathlib import Path

from src.event_journal import EventJournal


class TestEventJournal(unittest.TestCase):
    def test_events_are_persisted_and_read_in_arrival_order(self):
        with tempfile.TemporaryDirectory() as directory:
            journal_path = Path(directory) / "events.jsonl"
            journal = EventJournal(journal_path)

            events = [
                {"sequence": 2, "delivery_id": "B", "runs": 4},
                {"sequence": 1, "delivery_id": "A", "runs": 1},
            ]

            for event in events:
                journal.append(event)

            self.assertEqual(journal.read_all(), events)

    def test_journal_survives_reopening(self):
        with tempfile.TemporaryDirectory() as directory:
            journal_path = Path(directory) / "events.jsonl"
            event = {
                "sequence": 1,
                "delivery_id": "A",
                "runs": 4,
            }

            EventJournal(journal_path).append(event)

            reopened_journal = EventJournal(journal_path)
            self.assertEqual(reopened_journal.read_all(), [event])

    def test_invalid_json_record_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            journal_path = Path(directory) / "events.jsonl"
            journal_path.write_text("{invalid json}\n", encoding="utf-8")

            journal = EventJournal(journal_path)

            with self.assertRaisesRegex(ValueError, "line 1"):
                journal.read_all()


if __name__ == "__main__":
    unittest.main()
