def replay_event(events):
    score =0

    for event in events:
        score+=event["runs"]
    
    return score


event_a={"delivery_id": "event-A","runs":4}
event_b={"delivery_id": "event-B","runs":2}

replay_1=replay_event([event_a,event_b])
replay_2=replay_event([event_b,event_a])

print(f"Replay A then B: {replay_1}")
print(f"Replay B then A: {replay_2}")