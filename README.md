# MatchFeed Lab

MatchFeed Lab is a Python learning project focused on reliable cricket data ingestion, score reconstruction, and event replay.

The project explores how a data-processing system can handle duplicate events, delayed arrivals, missing events, and out-of-order delivery while maintaining a consistent score.

## Current Features

- Read and inspect cricket match data stored as JSON.
- Calculate innings runs, recorded wickets, and legal balls.
- Experiment with duplicate-event detection.
- Replay events in sequence order.
- Buffer out-of-order events until missing events arrive.
- Test core behavior using Python's `unittest` framework.

## Project Status

This project is an educational prototype. Its replay experiments use simplified event models and are not yet a production-grade cricket scoring system.

## Requirements

- Python 3.14 or a compatible Python version.
- A virtual environment is recommended.

## Run the Score Engine

From the project root:

```bash
python -m src.run_score_engine
```

## Run Tests

```bash
python -m unittest discover -s tests -v
```

## Data

The sample match JSON file is stored in `data/raw/sample_match.json`.

Check the original data source's attribution and licensing requirements before redistributing the dataset.

## Learning Objectives

- Data validation and ingestion
- Event ordering and replay
- Idempotency and duplicate detection
- Buffering and recovery from missing events
- Automated testing and maintainable Python design