
import tempfile
import unittest
from pathlib import Path

from src.event_journal import EventJournal
from src.correction_replay import CorrectionReplay


def make_event(delivery_id, sequence, total, batter=None):
    if batter is None:
        batter = total

    return {
        "type": "delivery",
        "sequence": sequence,
        "delivery_id": delivery_id,
        "delivery": {
            "runs": {
                "batter": batter,
                "extras": total - batter,
                "total": total,
            }
        },
    }


class TestCorrectionReplay(unittest.TestCase):
    def test_correction_replaces_original_delivery(self):
        with tempfile.TemporaryDirectory() as directory:
            journal = EventJournal(Path(directory) / "events.jsonl")

            journal.append(make_event("A", 1, 4))
            journal.append(make_event("B", 2, 2))

            journal.append({
                "type": "correction",
                "target_delivery_id": "A",
                "replacement": make_event("A", 1, 6),
            })

            state = CorrectionReplay(journal).replay()

            self.assertEqual(state["runs"], 8)
            self.assertEqual(state["deliveries"], 2)

    def test_correction_of_unknown_delivery_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            journal = EventJournal(Path(directory) / "events.jsonl")

            journal.append({
                "type": "correction",
                "target_delivery_id": "unknown",
                "replacement": make_event("unknown", 1, 6),
            })

            with self.assertRaisesRegex(ValueError, "unknown delivery"):
                CorrectionReplay(journal).replay()

    def test_original_journal_record_is_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            journal = EventJournal(Path(directory) / "events.jsonl")
            original = make_event("A", 1, 4)

            journal.append(original)
            journal.append({
                "type": "correction",
                "target_delivery_id": "A",
                "replacement": make_event("A", 1, 6),
            })

            records = journal.read_all()

            self.assertEqual(len(records), 2)
            self.assertEqual(records[0], original)
            self.assertEqual(records[1]["type"], "correction")


if __name__ == "__main__":
    unittest.main()
