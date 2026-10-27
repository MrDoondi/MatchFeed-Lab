
def replay_events(events, target):
    state = {
        "runs": 0,
        "innings_complete": False,
    }

    for event in events:
        if state["innings_complete"]:
            continue

        if event["type"] == "runs":
            state["runs"] += event["value"]

            if state["runs"] >= target:
                state["innings_complete"] = True

    return state


reach_target = {"type": "runs", "value": 5}
extra_runs = {"type": "runs", "value": 2}

print(
    "Target event then extra event:",
    replay_events([reach_target, extra_runs], target=5),
)

print(
    "Extra event then target event:",
    replay_events([extra_runs, reach_target], target=5),
)
