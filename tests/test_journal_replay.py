
import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from src.buffered_replay import BufferedReplay
from src.event_journal import EventJournal


class TestJournalReplay(unittest.TestCase):
    def test_saved_events_reconstruct_identical_replay_state(self):
        events = [
            {
                "sequence": 2,
                "delivery_id": "delivery-2",
                "delivery": {
                    "runs": {"batter": 4, "extras": 0, "total": 4}
                },
            },
            {
                "sequence": 1,
                "delivery_id": "delivery-1",
                "delivery": {
                    "runs": {"batter": 1, "extras": 0, "total": 1}
                },
            },
            {
                "sequence": 3,
                "delivery_id": "delivery-3",
                "delivery": {
                    "runs": {"batter": 0, "extras": 1, "total": 1},
                    "extras": {"wides": 1},
                },
            },
        ]

        with tempfile.TemporaryDirectory() as directory:
            journal = EventJournal(
                Path(directory) / "events.jsonl"
            )

            original_replay = BufferedReplay()

            # Record each event as it arrives and process it.
            with contextlib.redirect_stdout(io.StringIO()):
                for event in events:
                    journal.append(event)
                    original_replay.receive(event)

            # Rebuild the state using a fresh replay instance.
            restored_replay = BufferedReplay()

            with contextlib.redirect_stdout(io.StringIO()):
                for event in journal.read_all():
                    restored_replay.receive(event)

            self.assertEqual(restored_replay.score, original_replay.score)
            self.assertEqual(
                restored_replay.total_wickets,
                original_replay.total_wickets,
            )
            self.assertEqual(
                restored_replay.legal_balls,
                original_replay.legal_balls,
            )
            self.assertEqual(
                restored_replay.extra_runs,
                original_replay.extra_runs,
            )
            self.assertEqual(
                restored_replay.processed_events,
                original_replay.processed_events,
            )
            self.assertEqual(restored_replay.buffer, {})
            self.assertEqual(
                restored_replay.get_status()["status"], "caught_up"
            )

            self.assertEqual(restored_replay.score, 6)
            self.assertEqual(restored_replay.legal_balls, 2)
            self.assertEqual(restored_replay.extra_runs, 1)


if __name__ == "__main__":
    unittest.main()
