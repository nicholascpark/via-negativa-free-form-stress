# Independent audit — interactive trial v1

**Verdict: useful behavior demonstrated within this synthetic trial; no in-scope functional failure found.** Two replies selected consequential policies and changed the adopted build. The third confirmed policies already implemented provisionally. The candidate passed the frozen private cases and the auditor's preregistered cases. Question framing and standalone provenance wording have limitations. This is not evidence that the skill outperforms ordinary prompting or works with actual users.

## Protocol and independence

The [audit plan](preregistered-plan.md) preceded fixture inspection. The [four additional cases and metamorphic plan](holdout-plan.md) were frozen at **03:34:39 UTC**, before inspecting any builder artifact; candidate freeze was **03:42:45 UTC**. I inspected frozen relay snapshots, copied v3 into `audit/frozen-candidate`, and changed no candidate logic. [The portable runner](run_audit.py) verified **88 file hashes**, including setup, before-answer snapshots, candidate, and auditor commitments. All matched. The original six private cases were coherent with the frozen dossier; no fixture repair was needed.

The protocol says all three roles started with `fork_turns=none`; isolation was instructed file visibility, not OS-enforced. Roles share model priors. The harness explicitly required prospective answer/action records and version checkpoints and suggested 1–3 worthwhile question rounds. Their presence cannot be attributed solely to the skill. I sent no implementation guidance to the practitioner or simulated user.

## Question → answer → decision → artifact → check

| Round | Prior uncertainty and reply | Pre-answer commitment and observed consequence |
|---|---|---|
| 1 | Public `two_ports` did not establish physical identity. Reply: left/right are independently failing and recovering ducts; `ports-4` needs its own page. | [Question 01 snapshot](../relay/question-01-before-answer/question-01.md) maps independent sources to `(cabinet, port)` state. v0 already had cabinet and port alternatives; v1 made port scope mandatory. Executed lineage check: cabinet route pages `ports-3`; v1 pages `ports-3, ports-4`. This selected an existing branch, rather than inventing it after the reply. |
| 2 | Public `n` had no ordering/reset guarantee. Reply: per-duct monotonic counter including INVALID, durable through restarts, identical retries, current-condition semantics. | [Question 02 snapshot](../relay/question-02-before-answer/question-02.md) maps that contract to rejecting `n <= frontier` before state changes and includes alternative/reset/unknown outcomes. v1 had conditional filtering off by default; v2 enabled it. Executed check: default output changes from `reconnect-2, reconnect-4` to `reconnect-2`. |
| 3 | Qualified recovery, startup, unreadability, and reminders remained unconfirmed. Reply: one fresh NORMAL clears, initial HIGH pages, INVALID neither clears nor pages, no reminders. | [Question 03 snapshot](../relay/question-03-before-answer/question-03.md) promises finalization and boundary checks for that reply. v3 adds the final contract, reusable interface, trace, and checks. **No notification-policy change:** v2 and v3 agree on all 18 audited captures. Count this as confirmation, not adaptation. |

Root's question timestamps precede replies by 23.6, 35.9, and 28.1 seconds. Exact replies are in `relay/answer-01.json` through `answer-03.json`; executed artifact comparisons are in [lineage-checks.json](lineage-checks.json).

## Criteria

| Criterion | Judgment | Evidence and limitation |
|---|---|---|
| 1. Consequential information elicited | **Pass** | Three omitted operational fact groups were revealed; none was established by public data alone. Replies stayed consistent with the frozen dossier. |
| 2. Prospective mapping and adaptation | **Pass, qualified** | All mappings precede replies. Rounds 1–2 select consequential branches and affect the adopted build. Round 3 confirms rather than changes behavior. Logging is harness-scaffolded. |
| 3. Leadingness and user burden | **Partial** | Three topical rounds, no repeated settled question. Round 1 offers alternatives. Round 2 mildly suggests ignoring replay. Round 3 bundles four policies, presents preferred outputs, and asks “Does that match your needs”; this can encourage acquiescence. Alternatives are allowed, but a dossier-driven simulated user cannot validate real-human framing or burden. |
| 4. Continuous artifact development | **Pass** | Executable v0 alternatives → independently scoped v1 → source-order-enabled v2 → runnable, traced, tested v3. The objects develop beyond a suggestion list. This is a straightforward notifier redesign, not evidence of scientific novelty. |
| 5. Obligation-derived local cases | **Pass** | Three early development probes state rival predictions and unresolved premises. Final tests ground cases in actual replies. The 243-history test checks retry/time invariance using self-produced base output; it does not independently establish correct base decisions. Worker tests remain development evidence. |
| 6. Final commitments and withheld cases | **Pass in scope** | All eight public, six private, and four auditor cases passed; all preregistered transformations and batch/incremental checks passed. Full per-record before/after outputs regenerate. |
| 7. Evidence and scope honesty | **Partial** | Synthetic checks, deployment absence, in-memory limits, and unmeasured costs are disclosed. However v3 README says “actual technician replies” without explicitly identifying the technician as simulated. Parent answer records do say “actual simulated technician.” A standalone handoff should state simulation plainly. No claim of skill superiority is justified. |
| 8. Rough costs and interruptions | **Pass for observable costs** | Three simulated-user interruptions; 186 question words and 164 reply words. Setup freeze to candidate freeze: **9m 47s**, including coordination. Tokens, money, compute, and real-user interruption costs were not measured. |

## Executed results

Run from any directory: `PYTHONDONTWRITEBYTECODE=1 python3 audit/run_audit.py` with the script path resolved from the retained trial directory. Exit status **0**; detailed observations and expected/actual arrays are in [results.json](results.json).

- **Public: 8/8; private user: 6/6; auditor holdout: 4/4.** Private outputs were respectively `p1-2`; `p2-1,p2-2,p2-5`; `p3-1,p3-8`; `p4-1,p4-5`; `p5-1,p5-3,p5-4,p5-5`; `p6-1,p6-4`.
- **72/72 preregistered transformations passed**: compact/stretched receipt times, per-source affine counters, and consistent source relabeling over those 18 cases. These are related checks, not 72 independent scenarios. Repeated fresh batches, empty input, per-record preservation, and incremental/batch consistency also passed.
- Separately reran the **worker's 11 tests**, including its 243 generated histories: all passed. See [worker-test-rerun.txt](worker-test-rerun.txt).
- Table, JSON, and CSV CLI calls succeeded from outside the candidate directory. Saved JSON/CSV reproduced exactly and contained every public record.
- Public baseline comparison: 20-second cooldown emits **12** pages, with four unwanted repeats/replays and two missed required pages. The 60-second alternative emits **8**, still missing `quick-4` and `ports-4`. Candidate emits the required **10**. This supports a concrete behavioral improvement over the supplied algorithms, not a prompting-method comparison.

No material code defect was found under the fixed contract. The outstanding issues are the mildly leading bundled third question and ambiguous standalone description of the simulated speaker. Production behavior, unobserved physical recoveries, persistence, delivery reliability, counter resets outside the contract, and real-user effectiveness remain untested. The setup deliberately provides a small, answerable deterministic problem; one successful scripted run cannot establish general skill effectiveness.
