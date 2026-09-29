# Question 02 — source order

Pre-answer candidate: builder/v1/prototype.py, representation.md, streams.json, results.jsonl; parent v0 preserved. The source-order option is an explicit hypothesis, not adopted bench truth.

Exact user-facing question:
In `reconnected`, `reconnect-4` delivers HIGH with `n=51` after we already received NORMAL with `n=52`. Is that an old replay we should ignore, or can a genuinely new reading reuse a lower number? Specifically, is `n` an increasing counter independently for each duct, does it also reliably advance on INVALID records, and can it reset or wrap within these captures?

Prospective reply → pending action:
- Per-duct increasing counter, reliable through INVALID, no reset/wrap: adopt per-duct frontier and discard n <= frontier before state changes; INVALID advances frontier without implying recovery.
- Counter resets/wraps and epoch available: include epoch in ordering/identity under supplied semantics and test boundary.
- Counter resets/wraps with no epoch: do not pretend old replay and restart are distinguishable; leave delivery/source policies explicit and ask only if operational handling changes the usable result.
- Counter global or another scope: adjust frontier scope independently of per-duct episode scope, using supplied guarantees.
- INVALID n unreliable: do not advance frontier from INVALID without an alternative supported ordering contract.
- Unknown: retain the fork and disclose that filtering reconnect-4 is conditional.
