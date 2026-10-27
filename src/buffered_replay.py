from multiprocessing import Value
from typing import Sequence


class BufferedReplay:
    def __init__(self):
        self.expected_sequence=1
        self.score=0
        self.buffer={}
        self.processed_events={}

    def receive(self, event):
        sequence=event["sequence"]
        event_id=event["delivery_id"]

        if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence < 1:
            raise ValueError(f"Invalid sequence number: {sequence}")

        #handling duplicate squence with and without the same values

        if sequence in self.processed_events:
            if self.processed_events[sequence] == event:
                print(f"Ignoring duplicate event {sequence}")
                return
            raise ValueError(f"Conflicting event at sequence {sequence}")

        #handling buffered event with and without the same values

        if sequence in self.buffer:
            if self.buffer[sequence] == event:
                print(f"Ignoring duplicate buffered event {sequence}")
            raise ValueError(f"Conflicting buffered event at sequence {sequence}")

        #unprocessed older sequence\
        if sequence < self.expected_sequence:
            raise ValueError(f"Unexpected old sequence {sequence}")

        #buffering events
        self.buffer[sequence]=event

        if sequence > self.expected_sequence:
            print(f"Buffering event {sequence}; waiting for {self.expected_sequence}")
            return
        
        self._process_ready_events()

    def _process_ready_events(self):
        while self.expected_sequence in self.buffer:
            event = self.buffer.pop(self.expected_sequence)
            sequence = event["sequence"]

            self.score += event["runs"]
            self.processed_events[sequence] = event

            print(f"Processed event {sequence}; score = {self.score}")
            self.expected_sequence += 1
    

    def get_status(self):
        """Describe whether replay is caught up or waiting for events."""
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

    event_1 = {"sequence": 1, "delivery_id": "A", "runs": 2}
    event_2 = {"sequence": 2, "delivery_id": "B", "runs": 4}
    event_3 = {"sequence": 3, "delivery_id": "C", "runs": 1}

    # Deliberately deliver event 3 before event 2.
    replay.receive(event_1)
    replay.receive(event_3)
    replay.receive(event_2)

    print(f"Final score: {replay.score}")
    print(f"Next expected sequence: {replay.expected_sequence}")
    print(f"Events still buffered: {len(replay.buffer)}")

    stalled = BufferedReplay()
    stalled.receive(
        {"sequence": 1, "delivery_id": "A", "runs": 2}
    )
    stalled.receive(
        {"sequence": 3, "delivery_id": "C", "runs": 1}
    )

    print("Stalled replay status:", stalled.get_status())


if __name__ == "__main__":
    main()
