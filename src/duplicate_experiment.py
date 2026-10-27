
def process_event(score, event, processed_events):
    """Apply new events, ignore retries, and reject conflicts."""
    event_id = event["delivery_id"]
    runs = event["runs"]

    if event_id in processed_events:
        previous_runs = processed_events[event_id]

        if previous_runs != runs:
            raise ValueError(
                f"Conflicting payload for event ID {event_id}: "
                f"previously recorded {previous_runs} runs, "
                f"received {runs} runs"
            )

        return score

    score += runs
    processed_events[event_id] = runs

    return score


def main():
    score = 0
    processed_events = {}

    event_1 = {"delivery_id": "event-001", "runs": 4}
    event_2 = {"delivery_id": "event-002", "runs": 2}
    conflicting_event = {"delivery_id": "event-001", "runs": 6}

    score = process_event(score, event_1, processed_events)
    print(f"After first event: {score}")

    score = process_event(score, event_1, processed_events)
    print(f"After duplicate event: {score}")

    try:
        score = process_event(score, conflicting_event, processed_events)
    except ValueError as error:
        print(f"Conflict detected: {error}")

    print(f"Score after conflict: {score}")

    score = process_event(score, event_2, processed_events)
    print(f"After different event: {score}")


if __name__ == "__main__":
    main()
