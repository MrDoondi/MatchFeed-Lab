import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MATCH_FILE = PROJECT_ROOT/"data"/"raw"/"sample_match.json"

def main():
    with open(MATCH_FILE, "r", encoding='utf-8') as file:
        match = json.load(file)

        info=match["info"]

        print(f"Match type: {info["match_type"]}")
        print(f"Teams: {' , '.join(info["teams"])}")
        print(f"Date: {','.join(info[["dates"][0]])}")
        print(f"Venue: {info.get("venue", "Unknown")}")

        deliveries=[]

        for number, innings in enumerate(match["innings"], start=1):
            # for over in innings["overs"]:
            #     for delivery in over["deliveries"]:
            #         deliveries.append(delivery)


            deliveries=[
                delivery
                for over in innings["overs"]
                for delivery in over["deliveries"]
            ]
            # print(f"\n First delivery record: {deliveries[0]}")

            for delivery in deliveries:
                extras=delivery.get('extras', {})

                if 'wides' in extras or 'noballs' in extras:
                    print(f"delivery: {delivery['actual_delivery']}, extras:{extras}")
                    break

            Total_runs=sum(
                delivery["runs"]["total"]
                for delivery in deliveries
            )

            wickets=sum(
                len(delivery.get("wickets", []))
                for delivery in deliveries
            )
            
            print(f"\nInnings {number}: {innings["team"]}")
            print(f"Overs recorded : {len(innings["overs"])}")
            # print(f"deliveries recorded : {len(innings["overs"][0]["deliveries"])}")
            print(f"Delivery records: {len(deliveries)}")
            print(f"Runs in record ; {Total_runs}")
            print(f"Wickets recorded : {wickets}")
            # print()


            # print(Total_runs)
        
        # print(deliveries1)
        # print(deliveries)

if __name__ == "__main__":
    main()