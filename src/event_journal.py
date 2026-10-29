
import json
from pathlib import Path


class EventJournal:
    """Append events to a JSON Lines file and read them back."""

    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.touch(exist_ok=True)

    def append(self, event):
        """Persist one event as a JSON Lines record."""
        with self.path.open("a", encoding="utf-8") as file:
            file.write(
                json.dumps(event, sort_keys=True) + "\n"
            )

    def read_all(self):
        """Return journal events in their recorded arrival order."""
        events = []

        with self.path.open("r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                if not line.strip():
                    continue

                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError as error:
                    raise ValueError(
                        f"Invalid journal record at line {line_number}"
                    ) from error

        return events
