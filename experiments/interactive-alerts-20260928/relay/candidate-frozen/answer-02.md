# Answer 02
Source: actual simulated technician reply relayed by root.
Recorded by root: 2026-09-29T03:36:40.146414+00:00.
Scope: this synthetic bench/captures.

“`reconnect-4` is an old replay and should be ignored. `n` increases separately for each cabinet/duct, including INVALID records. It survives reconnects and restarts; it does not reset or wrap within these captures. Repeated numbers are retries of the same reading.

This notifier is for current conditions, so an older record should neither trigger a retroactive page nor clear a problem after a newer record has arrived.”

Adopted action: per-(cabinet,port) maximum accepted n; reject n <= maximum before any alarm transitions; fresh INVALID advances maximum. No historical replay/reconstruction. No inference about behavior beyond scoped captures or persistent notifier restart state.
