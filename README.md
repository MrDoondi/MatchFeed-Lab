# MatchFeed Lab

MatchFeed Lab is a Python-based cricket data engineering project focused on event ingestion, score reconstruction, ordered replay, buffering, duplicate detection, event journaling, and historical delivery corrections.

The project uses a sample cricket match in JSON format to explore how a replay system can reconstruct innings state when delivery events arrive out of order.

## Features

- **Score reconstruction:** Calculate runs, recorded wickets, legal balls, and extra runs.
- **Batch replay:** Process historical delivery events in sequence order.
- **Buffered replay:** Buffer out-of-order events until missing sequences arrive.
- **Duplicate detection:** Ignore identical repeated events and reject conflicting events.
- **Event validation:** Reject invalid sequence numbers and malformed scoring data.
- **Persistent event journal:** Store events as JSON Lines records and read them back in arrival order.
- **Deterministic replay:** Reconstruct the same replay state from a saved event journal.
- **Historical corrections:** Record correction events and rebuild aggregate innings state using the corrected delivery.
- **Automated testing:** Test core behavior, failure cases, journal persistence, corrections, and replay integration.

## Architecture

```text
Historical match JSON
        |
        v
Delivery Adapter
        |
        v
Batch Replay ---------> Score Engine
        |
        v
Buffered Replay
        |
        +----> Event Journal (JSONL)
        |
        +----> Correction Replay
        |
        v
Reconstructed innings state
        |
        v
Automated verification
```

The batch and buffered replay components demonstrate different processing strategies. The event journal preserves recorded events, while correction replay reconstructs aggregate state by applying corrections to previously recorded deliveries.

## Project Structure

```text
Matchfeed-lab/
├── data/
│   └── raw/
│       └── sample_match.json
├── src/
│   ├── buffered_replay.py
│   ├── correction_replay.py
│   ├── delivery_adapter.py
│   ├── event_journal.py
│   ├── innings_replay.py
│   ├── ordered_replay.py
│   ├── run_pipeline.py
│   ├── run_score_engine.py
│   ├── run_streaming_replay.py
│   └── score_engine.py
├── tests/
│   ├── test_buffered_replay.py
│   ├── test_correction_replay.py
│   ├── test_event_journal.py
│   ├── test_journal_replay.py
│   ├── test_ordered_replay.py
│   ├── test_pipeline.py
│   ├── test_score_engine.py
│   └── test_streaming_replay.py
├── .gitignore
└── README.md
```

## Requirements

- Python 3.14 or a compatible Python version.
- No third-party packages are required by the core project.

## Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## Run the Project

Run the score engine:

```bash
python -m src.run_score_engine
```

Verify batch replay against the sample match:

```bash
python -m src.run_pipeline
```

Verify buffered streaming replay:

```bash
python -m src.run_streaming_replay
```

Run the complete automated test suite:

```bash
python -m unittest discover -s tests -v
```

## Sample Verification Results

The sample match produces the following reconstructed innings totals:

| Team | Score | Legal balls | Extra runs | Delivery records |
|---|---:|---:|---:|---:|
| New Zealand | 180/5 | 120 | 9 | 128 |
| India | 181/6 | 119 | 10 | 126 |

Batch and buffered streaming verification have passed against the score-engine baseline for both innings. The automated suite has also passed 51 tests in the latest reported run.

## Engineering Concepts Demonstrated

- Event-driven data processing
- Ordered and buffered event replay
- Idempotency and conflict detection
- Input validation and error handling
- Persistent event journals
- Deterministic state reconstruction
- Correction events and replay-based score rebuilding
- Unit and integration testing
- Git-based version control

## Scope and Limitations

This is an educational prototype, not a production-grade cricket scoring platform.

- Streaming is simulated with deliberately reordered historical events; it is not a live feed consumer.
- Legal-ball calculation follows simplified rules based on wide and no-ball indicators.
- The event journal is a JSON Lines file, not a transactional database.
- Correction replay reconstructs aggregate innings state separately from the live buffered replay engine.
- Crash-safe transactions, concurrent ingestion, persistent checkpoints, and production monitoring are outside the current implementation.
- The included tests cover specified scenarios; they do not establish production readiness.

The sample data's source and redistribution licence should be checked before redistributing it.

## Project Goal

The goal of MatchFeed Lab is to learn and demonstrate reliable Python data processing through a concrete sports-data problem: reconstructing match state from delivery events despite ordering problems, duplicates, missing events, and historical corrections.
