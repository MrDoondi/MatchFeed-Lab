def calculate_total_runs(innings):
    """Calculate total runs, rejecting malformed delivery scores."""
    total_runs = 0

    for over in innings["overs"]:
        for delivery in over["deliveries"]:
            if "runs" not in delivery:
                raise ValueError("Delivery is missing 'runs'")

            runs = delivery["runs"]

            if not isinstance(runs, dict):
                raise ValueError("Delivery 'runs' must be a dictionary")

            if "total" not in runs:
                raise ValueError("Delivery runs is missing 'total'")

            total = runs["total"]

            if (
                not isinstance(total, int)
                or isinstance(total, bool)
                or total < 0
            ):
                raise ValueError(
                    "'runs.total' must be a non-negative integer"
                )

            total_runs += total

    return total_runs

def calculate_wickets(innings):

    total_wickets=0

    for over in innings['overs']:
        for delivery in over['deliveries']:
            total_wickets+=len(delivery.get('wickets',[]))
    
    return total_wickets

def calculate_legal_balls(innings):

    legal_balls=0

    for over in innings['overs']:
        for delivery in over['deliveries']:
            extras=delivery.get("extras",{})

            is_wide="wides" in extras
            is_no_ball="noballs" in extras

            if not is_no_ball and not is_wide:
                legal_balls+=1
    
    return legal_balls
