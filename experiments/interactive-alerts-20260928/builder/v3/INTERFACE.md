# Executable interface — frozen candidate v3

Working directory: `/private/tmp/via-negativa-interactive-20260928/builder/v3`
Python: 3.10+, standard library only.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 notifier.py
PYTHONDONTWRITEBYTECODE=1 python3 notifier.py streams.json --format json
PYTHONDONTWRITEBYTECODE=1 python3 notifier.py streams.json --format csv
PYTHONDONTWRITEBYTECODE=1 python3 test_notifier.py
```

The optional positional input path is a JSON object mapping capture names to lists of events in delivery order. Each event has `id` (unique string within capture), `t` (receipt seconds), `cabinet` and `port` (string labels), `n` (integer per-duct counter), and `reading` (`HIGH`, `NORMAL`, `INVALID`). Counter/order semantics are stated in README. Each capture starts with fresh memory. The default input is the colocated `streams.json`, regardless of shell working directory.

Import from a Python process with this directory on `sys.path`:

```python
from notifier import page_ids, decisions, Notifier, compare
page_ids(events)       # list[str], fresh state, candidate page IDs in delivery order
rows = decisions(events)  # one output dict per delivered event, fresh state
notifier = Notifier()
row = notifier.process(event)  # incremental state across calls
report = compare(streams)      # {'summary': [...], 'records': [...]}
```

`decisions`/`process` output preserves input keys and adds `fresh`, `page`, `reason`, `active_before`, `active_after`, and `newest_n_after`. `fresh=False` means n <= the prior per-duct frontier. Reason values: `ignored_non_newer`, `new_problem`, `continuing_problem`, `normal`, `recovered`, `unreadable_preserves_episode`.

`compare` adds capture labels and `cooldown20_page`/`cooldown60_page` to trace records. Summary rows have `capture`, `cooldown20`, `cooldown60`, and `candidate` lists. CSV uses `page` for the candidate decision. Unsupported reading values and noninteger counters raise ValueError; malformed files otherwise use ordinary Python exceptions. The interface expects the declared input schema and is not a production ingest validator.

Candidate immutability: SHA-256 of each candidate file is recorded in `manifest.json`; files/directories are read-only after checks. Any revision must be saved under a new version directory, leaving this version intact. Running with PYTHONDONTWRITEBYTECODE avoids cache writes in this snapshot.
