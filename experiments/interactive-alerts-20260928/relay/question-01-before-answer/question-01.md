# Question 01 — physical identity and paging scope

Pre-answer candidate: builder/v0/explore.py, results.jsonl, baseline.py, streams.json. Working question/representation: brief.md v0. Candidate is exploratory, not proposed final.

Exact user-facing question:
In `two_ports`, `ports-3` says A/left is HIGH and `ports-4` says A/right is HIGH three seconds later. Should `ports-4` create a separate page, or is it another view of the same problem? What do “left” and “right” physically represent, and can their readings recover independently? Another interpretation is welcome.

Prospective reply → pending action:
- Independent physical fault sources: key episodes and accepted source evidence by (cabinet, port); right onset pages separately.
- Two views of one shared condition: investigate how observations combine before implementing cabinet episode; do not clear a cabinet from a single port without knowing the aggregation rule.
- Port labels alias/move physical sources: introduce explicit source identity/mapping if observable; do not assume label equals physical fault identity.
- Unsure/other: preserve competing scope outputs and make unresolved scope explicit; use supplied operational examples to select next question.

Independent work while pending: inspect counter/INVALID/startup trajectories, construct ordering-sensitive cases without deciding their truth, keep 20/60 comparison competitive.
