
import unittest

from src.buffered_replay import BufferedReplay


class TestBufferedReplay(unittest.TestCase):
    def test_buffers_and_processes_events_in_order(self):
        replay = BufferedReplay()

        replay.receive(
            {"sequence": 1, "delivery_id": "A", "runs": 2}
        )
        replay.receive(
            {"sequence": 3, "delivery_id": "C", "runs": 1}
        )

        self.assertEqual(replay.score, 2)
        self.assertIn(3, replay.buffer)

        replay.receive(
            {"sequence": 2, "delivery_id": "B", "runs": 4}
        )

        self.assertEqual(replay.score, 7)
        self.assertEqual(replay.expected_sequence, 4)
        self.assertEqual(replay.buffer, {})

    def test_duplicate_event_does_not_add_runs_twice(self):
        replay = BufferedReplay()
        event = {"sequence": 1, "delivery_id": "A", "runs": 4}

        replay.receive(event)
        replay.receive(event)

        self.assertEqual(replay.score, 4)

    def test_conflicting_event_at_same_sequence_is_rejected(self):
        replay = BufferedReplay()

        replay.receive(
            {"sequence": 1, "delivery_id": "A", "runs": 4}
        )

        with self.assertRaisesRegex(ValueError, "Conflicting event"):
            replay.receive(
                {"sequence": 1, "delivery_id": "A", "runs": 6}
            )

        self.assertEqual(replay.score, 4)
    
    def test_reports_stalled_replay(self):
        replay = BufferedReplay()

        replay.receive(
            {"sequence": 1, "delivery_id": "A", "runs": 2}
        )
        replay.receive(
            {"sequence": 3, "delivery_id": "C", "runs": 1}
        )

        status = replay.get_status()

        self.assertEqual(
            status["status"], "waiting_for_missing_event"
        )
        self.assertEqual(status["next_expected_sequence"], 2)
        self.assertEqual(status["buffered_sequences"], [3])
        self.assertEqual(replay.score, 2)

    def test_recovers_after_missing_event_arrives(self):
        replay = BufferedReplay()

        replay.receive(
            {"sequence": 1, "delivery_id": "A", "runs": 2}
        )
        replay.receive(
            {"sequence": 3, "delivery_id": "C", "runs": 1}
        )
        replay.receive(
            {"sequence": 2, "delivery_id": "B", "runs": 4}
        )

        status = replay.get_status()

        self.assertEqual(replay.score, 7)
        self.assertEqual(status["status"], "caught_up")
        self.assertEqual(status["next_expected_sequence"], 4)
        self.assertEqual(status["buffered_sequences"], [])

    
    def test_conflicting_buffered_event_is_rejected(self):
        replay = BufferedReplay()

        original = {
            "sequence": 3,
            "delivery_id": "C",
            "runs": 1,
        }
        conflicting = {
            "sequence": 3,
            "delivery_id": "C",
            "runs": 4,
        }

        replay.receive(original)

        with self.assertRaisesRegex(
            ValueError, "Conflicting buffered event"
        ):
            replay.receive(conflicting)

        self.assertEqual(replay.score, 0)
        self.assertEqual(replay.buffer[3], original)
        self.assertEqual(replay.expected_sequence, 1)

    
    def test_rejects_zero_sequence(self):
        replay = BufferedReplay()

        with self.assertRaisesRegex(
            ValueError, "Invalid sequence number"
        ):
            replay.receive(
                {"sequence": 0, "delivery_id": "A", "runs": 4}
            )

        self.assertEqual(replay.score, 0)
        self.assertEqual(replay.buffer, {})

    def test_rejects_negative_sequence(self):
        replay = BufferedReplay()

        with self.assertRaisesRegex(
            ValueError, "Invalid sequence number"
        ):
            replay.receive(
                {"sequence": -1, "delivery_id": "A", "runs": 4}
            )

        self.assertEqual(replay.score, 0)
        self.assertEqual(replay.buffer, {})




if __name__ == "__main__":
    unittest.main()
