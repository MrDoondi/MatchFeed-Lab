def build_delivery_events(innings, innings_number):

    events = []
    sequence = 1

    for over in innings["overs"]:
        for delivery in over["deliveries"]:
            events.append({
                "sequence":sequence,
                "innings_number":innings_number,
                "delivery":delivery
            })
            sequence+=1

    return events