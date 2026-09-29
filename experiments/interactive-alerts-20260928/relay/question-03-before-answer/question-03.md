# Question 03 — episode/recovery policy

Pre-answer candidate: builder/v2/prototype.py, representation.md, streams.json, results.jsonl. Parent v1 preserved; per-duct counter filtering is now grounded in answer 02, remaining policies are provisional.

Exact user-facing question:
What counts as recovery on this bench: is one new NORMAL reading enough, or can NORMAL briefly flicker during a continuing problem? My candidate would page the first fresh HIGH even at startup, treat INVALID as “recovery unknown,” and send no further HIGH page until a fresh NORMAL has cleared that duct. That would page `startup-1` only and `invalid-2` only in those captures. Does that match your needs, or do you need repeat reminders or a different recovery rule?

Prospective reply → pending action:
- One NORMAL is trustworthy, INVALID is no evidence of recovery, initial HIGH deserves a page, no reminders: finalize these state transitions; generate reset/replay/startup/INVALID boundary checks.
- NORMAL can flicker: seek supplied debounce/hysteresis contract; expose candidate behavior and a concrete pending observation instead of inventing a threshold.
- INVALID constitutes recovery or an episode break: revise transition explicitly and test subsequent HIGH accordingly; keep ordering frontier independent.
- Initial HIGH should not page: introduce observed-NORMAL arming condition and document possible startup miss.
- Reminders required: distinguish initial/recurrent episode pages from scheduled reminders, preserve recurrence after recovery; implement only a user-specified schedule or keep reminder policy unresolved.
- Unsure/other: keep policy clearly provisional, show competing record-level output, and avoid declaring an operationally agreed rule.
