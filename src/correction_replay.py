
from src.event_journal import EventJournal


class CorrectionReplay:
    """Reconstruct delivery state from an append-only event journal."""

    def __init__(self, journal):
        self.journal = journal

    def replay(self):
        deliveries = {}

        for event in self.journal.read_all():
            event_type = event.get("type", "delivery")

            if event_type == "delivery":
                delivery_id = event.get("delivery_id")

                if not delivery_id:
                    raise ValueError(
                        "Delivery event is missing 'delivery_id'"
                    )

                if delivery_id in deliveries:
                    if deliveries[delivery_id] == event:
                        continue

                    raise ValueError(
                        f"Conflicting delivery ID: {delivery_id}"
                    )

                deliveries[delivery_id] = event

            elif event_type == "correction":
                target_id = event.get("target_delivery_id")

                if target_id not in deliveries:
                    raise ValueError(
                        f"Cannot correct unknown delivery: {target_id}"
                    )

                corrected = event.get("replacement")

                if not isinstance(corrected, dict):
                    raise ValueError(
                        "Correction must contain a replacement event"
                    )

                if corrected.get("delivery_id") != target_id:
                    raise ValueError(
                        "Replacement must preserve the original delivery ID"
                    )

                # Preserve the delivery's identity but replace its content.
                corrected_event = {
                    **corrected,
                    "type": "delivery",
                }

                deliveries[target_id] = corrected_event

            else:
                raise ValueError(f"Unknown event type: {event_type}")

        return self._calculate_state(deliveries.values())

    @staticmethod
    def _calculate_state(events):
        runs = 0
        wickets = 0
        legal_balls = 0
        extra_runs = 0

        for event in events:
            delivery = event.get("delivery")

            if not isinstance(delivery, dict):
                raise ValueError("Delivery event must contain a delivery")

            run_data = delivery.get("runs")
            if not isinstance(run_data, dict):
                raise ValueError("Delivery 'runs' must be a dictionary")

            total = run_data.get("total")
            extras_total = run_data.get("extras", 0)

            for name, value in (
                ("runs.total", total),
                ("runs.extras", extras_total),
            ):
                if (
                    not isinstance(value, int)
                    or isinstance(value, bool)
                    or value < 0
                ):
                    raise ValueError(
                        f"'{name}' must be a non-negative integer"
                    )

            extras = delivery.get("extras", {})
            if not isinstance(extras, dict):
                raise ValueError("'extras' must be a dictionary")

            wickets_data = delivery.get("wickets", [])
            if not isinstance(wickets_data, list):
                raise ValueError("'wickets' must be a list")

            runs += total
            extra_runs += extras_total
            wickets += len(wickets_data)

            if "wides" not in extras and "noballs" not in extras:
                legal_balls += 1

        return {
            "runs": runs,
            "wickets": wickets,
            "legal_balls": legal_balls,
            "extra_runs": extra_runs,
            "deliveries": len(list(events)),
        }
