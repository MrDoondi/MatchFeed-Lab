
import unittest

from src.buffered_replay import BufferedReplay


class TestBufferedReplay(unittest.TestCase):

    # Existing tests: simple event compatibility

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

    # New tests: full cricket delivery events

    @staticmethod
    def make_delivery_event(
        sequence,
        delivery_id,
        total,
        batter=0,
        extras=0,
        extra_types=None,
        wickets=None,
    ):
        delivery = {
            "runs": {
                "batter": batter,
                "extras": extras,
                "total": total,
            }
        }

        if extra_types:
            delivery["extras"] = extra_types

        if wickets is not None:
            delivery["wickets"] = wickets

        return {
            "sequence": sequence,
            "delivery_id": delivery_id,
            "delivery": delivery,
        }

    def test_reconstructs_runs_wickets_legal_balls_and_extras(self):
        replay = BufferedReplay()

        replay.receive(self.make_delivery_event(
            1, "A", total=1, extras=1,
            extra_types={"wides": 1},
        ))
        replay.receive(self.make_delivery_event(
            2, "B", total=4, batter=4,
        ))
        replay.receive(self.make_delivery_event(
            3, "C", total=0,
            wickets=[{"kind": "bowled", "player_out": "Batter"}],
        ))

        self.assertEqual(replay.score, 5)
        self.assertEqual(replay.total_wickets, 1)
        self.assertEqual(replay.legal_balls, 2)
        self.assertEqual(replay.extra_runs, 1)
        self.assertEqual(replay.expected_sequence, 4)

    def test_buffered_delivery_events_recover_in_order(self):
        replay = BufferedReplay()

        event_1 = self.make_delivery_event(1, "A", total=1, batter=1)
        event_2 = self.make_delivery_event(
            2, "B", total=1, extras=1,
            extra_types={"wides": 1},
        )
        event_3 = self.make_delivery_event(3, "C", total=4, batter=4)

        replay.receive(event_1)
        replay.receive(event_3)

        self.assertEqual(replay.score, 1)
        self.assertEqual(replay.legal_balls, 1)
        self.assertEqual(replay.buffer, {3: event_3})

        replay.receive(event_2)

        self.assertEqual(replay.score, 6)
        self.assertEqual(replay.legal_balls, 2)
        self.assertEqual(replay.extra_runs, 1)
        self.assertEqual(replay.expected_sequence, 4)
        self.assertEqual(replay.buffer, {})

    def test_identical_buffered_event_is_ignored(self):
        replay = BufferedReplay()

        replay.receive(
            self.make_delivery_event(3, "C", total=4, batter=4)
        )
        original_buffer = dict(replay.buffer)

        # An exact duplicate should not raise or alter the buffer.
        replay.receive(
            self.make_delivery_event(3, "C", total=4, batter=4)
        )

        self.assertEqual(replay.buffer, original_buffer)
        self.assertEqual(replay.score, 0)
        self.assertEqual(replay.expected_sequence, 1)

    def test_conflicting_full_delivery_at_buffered_sequence_is_rejected(self):
        replay = BufferedReplay()

        replay.receive(
            self.make_delivery_event(3, "C", total=1, batter=1)
        )

        with self.assertRaisesRegex(
            ValueError, "Conflicting buffered event"
        ):
            replay.receive(
                self.make_delivery_event(3, "C", total=4, batter=4)
            )

        self.assertEqual(replay.score, 0)
        self.assertEqual(replay.expected_sequence, 1)

    def test_no_ball_adds_runs_but_not_a_legal_ball(self):
        replay = BufferedReplay()

        replay.receive(self.make_delivery_event(
            1, "A", total=2, batter=1, extras=1,
            extra_types={"noballs": 1},
        ))

        self.assertEqual(replay.score, 2)
        self.assertEqual(replay.extra_runs, 1)
        self.assertEqual(replay.legal_balls, 0)

    def test_invalid_delivery_total_is_rejected(self):
        replay = BufferedReplay()

        event = {
            "sequence": 1,
            "delivery_id": "A",
            "delivery": {
                "runs": {"batter": 0, "extras": 0, "total": -1}
            },
        }

        with self.assertRaisesRegex(
            ValueError, "runs.total"
        ):
            replay.receive(event)

        self.assertEqual(replay.score, 0)
        self.assertEqual(replay.buffer, {})


if __name__ == "__main__":
    unittest.main()
