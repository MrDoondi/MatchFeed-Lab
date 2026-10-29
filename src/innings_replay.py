from functools import total_ordering
from typing import Sequence


def replay_innings(events, team):
    ordered_events= sorted(events, key=lambda event:event["sequence"])

    total_runs=0
    total_wickets=0
    legal_balls=0
    expected_sequence=1
    extra_runs=0

    for event in ordered_events:
        sequence = event['sequence']

        if sequence!=expected_sequence:
            raise ValueError(f"Expected sequence {expected_sequence} got sequence {sequence}")


        delivery=event['delivery']

        total_runs+=delivery["runs"]["total"]
        total_wickets+=len(delivery.get('wickets',[]))
        extras = delivery.get('extras',{})
        extra_runs+=delivery["runs"]["extras"]

        is_wide="wides" in extras
        is_no_ball="noballs" in extras

        if not is_no_ball and not is_wide:
            legal_balls+=1

        expected_sequence+=1

    return {
        "team":team,
        "runs":total_runs,
        "wickets":total_wickets,
        "legal_balls":legal_balls,
        "deliveries_processed":len(ordered_events),
        "extra_runs":extra_runs
    }