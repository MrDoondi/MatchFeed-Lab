def replay_events(events):
    ordered_events = sorted(
        events,
        key=lambda event: event["sequence"],
    )

    expected_sequence = 1
    score = 0

    for event in ordered_events:
        sequence = event["sequence"]

        if sequence < expected_sequence:
            raise ValueError(
                f"Duplicate sequence number: {sequence}"
            )

        if sequence > expected_sequence:
            raise ValueError(
                f"Missing event: expected sequence "
                f"{expected_sequence}, got {sequence}"
            )

        score += event["runs"]
        expected_sequence += 1

    return score

def main():
    events = [
        {"sequence": 1, "delivery_id": "event-A", "runs": 2},
        {"sequence": 2, "delivery_id": "event-B", "runs": 4},
        {"sequence": 2, "delivery_id": "event-C", "runs": 1},
        {"sequence": 3, "delivery_id": "event-D", "runs": 2},
    ]

    print("Replay score:", replay_events(events))

if __name__=="__main__":
    main()
