from multiprocessing import Value
from typing import Sequence



class BufferedReplay:
    def __init__(self):
        self.expected_sequence = 1
        self.score = 0
        self.total_wickets = 0
        self.legal_balls = 0
        self.extra_runs = 0
        self.buffer = {}
        self.processed_events = {}

    def receive(self, event):
        sequence = event["sequence"]

        if (
            not isinstance(sequence, int)
            or isinstance(sequence, bool)
            or sequence < 1
        ):
            raise ValueError(f"Invalid sequence number: {sequence}")

        if "delivery_id" not in event:
            raise ValueError("Event is missing 'delivery_id'")

        # Validate the event payload before buffering it.
        if "delivery" in event:
            delivery = event["delivery"]

            if not isinstance(delivery, dict):
                raise ValueError("'delivery' must be a dictionary")

            runs = delivery.get("runs")
            if not isinstance(runs, dict):
                raise ValueError("Delivery 'runs' must be a dictionary")

            total = runs.get("total")
            extras_total = runs.get("extras", 0)

            if (
                not isinstance(total, int)
                or isinstance(total, bool)
                or total < 0
            ):
                raise ValueError(
                    "'runs.total' must be a non-negative integer"
                )

            if (
                not isinstance(extras_total, int)
                or isinstance(extras_total, bool)
                or extras_total < 0
            ):
                raise ValueError(
                    "'runs.extras' must be a non-negative integer"
                )

            wickets = delivery.get("wickets", [])
            if not isinstance(wickets, list):
                raise ValueError("'wickets' must be a list")

        elif "runs" in event:
            # Compatibility with the original simple replay experiments.
            runs = event["runs"]
            if (
                not isinstance(runs, int)
                or isinstance(runs, bool)
                or runs < 0
            ):
                raise ValueError("'runs' must be a non-negative integer")
        else:
            raise ValueError("Event must contain 'delivery' or 'runs'")

        # Duplicate already processed.
        if sequence in self.processed_events:
            if self.processed_events[sequence] == event:
                print(f"Ignoring duplicate event {sequence}")
                return
            raise ValueError(f"Conflicting event at sequence {sequence}")

        # Duplicate already buffered.
        if sequence in self.buffer:
            if self.buffer[sequence] == event:
                print(f"Ignoring duplicate buffered event {sequence}")
                return
            raise ValueError(f"Conflicting buffered event at sequence {sequence}")

        if sequence < self.expected_sequence:
            raise ValueError(f"Unexpected old sequence {sequence}")

        self.buffer[sequence] = event

        if sequence > self.expected_sequence:
            print(
                f"Buffering event {sequence}; "
                f"waiting for {self.expected_sequence}"
            )
            return

        self._process_ready_events()

    def _process_ready_events(self):
        while self.expected_sequence in self.buffer:
            event = self.buffer.pop(self.expected_sequence)

            if "delivery" in event:
                delivery = event["delivery"]
                runs = delivery["runs"]

                self.score += runs["total"]
                self.extra_runs += runs.get("extras", 0)
                self.total_wickets += len(delivery.get("wickets", []))

                extras = delivery.get("extras", {})
                is_wide = "wides" in extras
                is_no_ball = "noballs" in extras

                if not is_wide and not is_no_ball:
                    self.legal_balls += 1

            else:
                self.score += event["runs"]

            sequence = event["sequence"]
            self.processed_events[sequence] = event

            print(f"Processed event {sequence}; score = {self.score}")
            self.expected_sequence += 1

    def get_status(self):
        if not self.buffer:
            return {
                "status": "caught_up",
                "next_expected_sequence": self.expected_sequence,
                "buffered_sequences": [],
            }

        return {
            "status": "waiting_for_missing_event",
            "next_expected_sequence": self.expected_sequence,
            "buffered_sequences": sorted(self.buffer),
        }


def main():
    replay = BufferedReplay()

    events = [
        {
            "sequence": 1,
            "delivery_id": "A",
            "delivery": {
                "runs": {"batter": 0, "extras": 1, "total": 1},
                "extras": {"wides": 1},
            },
        },
        {
            "sequence": 2,
            "delivery_id": "B",
            "delivery": {
                "runs": {"batter": 4, "extras": 0, "total": 4},
            },
        },
    ]

    replay.receive(events[0])
    replay.receive(events[1])

    print(f"Final score: {replay.score}/{replay.total_wickets}")
    print(f"Legal balls: {replay.legal_balls}")
    print(f"Extra runs: {replay.extra_runs}")
    print("Replay status:", replay.get_status())


if __name__ == "__main__":
    main()
