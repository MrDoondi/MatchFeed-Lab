def calculate_total_runs(innings):

    Total_runs=0

    for over in innings['overs']:
        for delivery in over['deliveries']:
            Total_runs+=delivery['runs']['total']
    
    return Total_runs

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
