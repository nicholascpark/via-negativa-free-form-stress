# Duct episode notifier — candidate v3

Use one alarm episode per `(cabinet, port)`, admitted by source freshness. Raising the cooldown to 60 seconds would suppress repeated pages here, but would still miss the confirmed new problem at `quick-4` and the independent right-duct problem at `ports-4`.

For each duct, remember the newest accepted `n` and whether a problem is active:

1. Ignore a row with `n` no greater than that duct's newest accepted counter. It cannot page, clear, or alter the freshness frontier.
2. Otherwise advance the counter, including for INVALID.
3. HIGH pages if no problem is active and then marks it active. This includes first-ever HIGH.
4. NORMAL clears the active problem immediately. A following fresh HIGH may page immediately.
5. INVALID leaves the episode unchanged and does not page. Elapsed time never clears an episode or causes reminders.

An inactive bit before any readable sample does **not** assert the duct is healthy; it only means no active episode has yet been observed. A fresh initial HIGH still pages. Receipt order is preserved; no sorting fabricates a historical timeline.

## Before and after

| Capture | Current 20 seconds | Cooldown 60 seconds | Candidate |
|---|---|---|---|
| long_spell | long-2, long-4 | long-2 | long-2 |
| quick_return | quick-2 | quick-2 | quick-2, quick-4 |
| two_ports | ports-3 | ports-3 | ports-3, ports-4 |
| reconnected | reconnect-2, reconnect-4 | reconnect-2 | reconnect-2 |
| unreadable_patch | invalid-2, invalid-4 | invalid-2 | invalid-2 |
| quiet | none | none | none |
| already_high | startup-1, startup-2 | startup-1 | startup-1 |
| two_cabinets | cabs-3, cabs-4 | cabs-3, cabs-4 | cabs-3, cabs-4 |

The candidate adds `quick-4` and `ports-4`; removes `long-4`, `reconnect-4`, `invalid-4`, and `startup-2`. All other record decisions match the current baseline. The total falls from 12 to 10, but the important change is which problems are represented. The 60-second baseline emits 8 and still misses both required pages.

`records.csv` and `comparison.json` include **every delivered row**, the two baseline decisions, candidate decision, reason, freshness admission, and state after processing. The table can be regenerated with `python3 notifier.py`; use `--format csv` or `--format json` for full records. `baseline.py` and `streams.json` are unmodified copies of the supplied public inputs.

## Confirmed operating contract

These are actual technician replies relayed by root for this synthetic bench/captures, not inferred truths about extraction hardware:

- Answer 01, 2026-09-29 03:34:44 UTC: ports are independent ducts, recover independently, and `ports-4` deserves a page.
- Answer 02, 2026-09-29 03:36:40 UTC: `n` increases independently per cabinet/duct, includes INVALID, survives reconnect/restart, and does not reset/wrap in these captures. Equal counters are retries. Older rows must neither page retrospectively nor clear newer conditions.
- Answer 03, 2026-09-29 03:38:29 UTC: HIGH/NORMAL are qualified upstream; one fresh NORMAL is recovery even if brief. Page initial HIGH; INVALID neither proves recovery nor needs a page; no reminders even after long silence.

Exact replies and prospective question/action mappings are preserved in the parent builder directory. v0 compared time versus episode scopes; v1 adopted independent ducts and explored source order; v2 adopted source freshness; v3 finalizes the confirmed episode policy and adds a usable trace interface and checks. Those parent candidates remain available.

## Checks and limits

Run `PYTHONDONTWRITEBYTECODE=1 python3 test_notifier.py`. Eleven tests pass, covering all eight supplied captures plus generated retry/time-invariance checks over 243 five-reading histories. Other cases exercise stale NORMAL, INVALID advancing the frontier, initial unreadability, independent ducts/cabinets, immediate recurrence, very long silence, fresh capture memory, and incremental processing. Expected behavior is tied to the technician contract; these are synthetic development checks, not held-out evidence or real-bench validation. `checks.txt` preserves actual results.

Tradeoffs follow the agreed purpose: a valid brief NORMAL rearms immediately, so truly alternating qualified states can page frequently. Missing recovery observations can merge two physical problems into one observed episode. Old source history is discarded deliberately. No reminder or unreadability alarm is generated. A fresh notifier instance will page an initial HIGH even if an earlier process already paged it.

The offline task is complete under the confirmed contract. Before adapting this to a continuously running bench, the remaining facts are how stable duct identity and counter ordering remain outside these captures, whether notifier memory must survive process restarts, and what delivery acknowledgement/retry behavior the paging channel requires. This prototype has in-memory state only, prints decisions, and does not send pages, guarantee notification delivery, or deploy anything. Runtime is Python 3.10+ and the standard library; no hardware, network, paid calls, or external services were used. Full resource/token cost was not measured.
