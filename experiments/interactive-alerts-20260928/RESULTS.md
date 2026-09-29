# Interactive fresh-context trial — 2026-09-28

**The skill produced useful behavior in this synthetic task.** The independent
auditor found no functional defect within the fixed contract. Two user replies
affected the adopted build; the third confirmed behavior already proposed.
Question framing and the candidate's standalone description of its simulated
user received partial findings. The frozen candidate and skill are unchanged.

Read the [actual question/answer transcript](TRANSCRIPT.md),
[independent audit](audit/audit.md), or
[runnable final candidate](relay/candidate-frozen/v3/notifier.py).
The [corrected standalone handoff](HANDOFF.md) makes the simulated speaker
explicit without changing any frozen candidate or evidence file.

## What was tested

Three new agents were spawned with `fork_turns=none`: a practitioner using the
latest skill, a simulated technician, and an auditor. The technician created a
small instrumentation task plus private operating facts and six withheld cases.
Those inputs were frozen before the practitioner started. The auditor committed
four additional cases and transformation rules before inspecting the build.

The public task proposed raising a notifier's cooldown from 20 to 60 seconds
because it repeatedly paged during one fault while missing some subsequent
faults. The practitioner received the current code and eight synthetic captures.
It received no expected implementation or private case answers. Each question,
prospective answer-to-action map, and current artifact was copied and hashed
before the simulated technician answered. The final artifact was frozen before
independent testing. See [protocol](protocol.json) and [event log](relay/events.jsonl).

## The interaction changed concrete decisions

| Question topic | Previously unavailable answer | Consequence |
|---|---|---|
| Physical identity | Left/right are independently failing and recovering ducts | Select separate per-duct episodes; restore the right-duct page |
| Source ordering | Counters increase per duct, include INVALID, and identify retries | Activate freshness admission before state changes; suppress a replayed HIGH and prevent stale recovery |
| Recovery/startup/reminders | One qualified NORMAL clears; initial HIGH pages; INVALID does not clear; reminders unwanted | Confirm existing provisional rules and generate checks; no observed policy change |

The first two answers selected alternatives already being explored. The broader
idea of episodes existed before those replies. The evidence supports consequential
selection and refinement, not a claim that the replies originated the whole design.

The practitioner generated tests for stale NORMAL records, fresh recovery followed
by immediate recurrence, INVALID advancing source order without clearing a fault,
and source independence. That is a concrete local benchmark growing from the
developing representation and the answers. The auditor tested additional cases
the practitioner had never received.

## Executed evidence

| Evidence group | Result |
|---|---:|
| Public scenarios | 8/8 |
| Previously private technician scenarios | 6/6 |
| Additional auditor scenarios | 4/4 |
| Preregistered transformations of those scenarios | 72/72 |
| Practitioner's development tests, independently rerun | 11/11 |
| Provenance file-hash checks | 88/88 |

The 72 transformations are related checks, not 72 independent tasks. The worker's
243 generated histories check invariance; they are not independent ground-truth
cases. Batch/incremental behavior, empty input, CLI modes, and saved output
reproduction also passed. Detailed expected and observed values are in
[audit/results.json](audit/results.json).

Across the 33 public input records:

| Implementation | Required pages missed | Unwanted repeat/replay pages |
|---|---:|---:|
| Existing 20-second cooldown | 2 | 4 |
| Proposed 60-second cooldown | 2 | 0 |
| Final per-duct episode notifier | 0 | 0 |

The simulated technician selected the prototype over the longer cooldown after
reading those concrete outputs. That is role-play feedback, not real-user evidence.

## Audit limitations and findings

- Question 03 bundles several policies and preferred outputs before asking for
  agreement. A less suggestive follow-up should first ask how recovery and reminders
  work, then compare consequences. The simulated user's frozen facts protected
  this run from preference drift; they cannot measure human acquiescence.
- The frozen candidate README says "actual technician replies" without plainly
  saying the technician was simulated. Its parent answer records are clearer.
  Every technician statement in this trial was simulated. This wrapper corrects
  the provenance description without rewriting the audited artifact.
- The harness explicitly requested prospective records and checkpoints, so those
  behaviors are partly scaffolded. There is no ordinary-prompting control arm,
  and the roles share model priors. This trial cannot identify the skill's marginal
  effect or establish scientific novelty, general effectiveness, or performance
  with actual users.
- Isolation used fresh conversation contexts and instructed file boundaries;
  it was not enforced through separate OS permissions.
- There were three question rounds, totaling 186 question words and 164 reply
  words. Setup freeze to candidate freeze was 9m 47s including coordination.
  Tokens, money, compute, and actual human burden were not measured.

No deployment, physical experiment, external data access, or page delivery took
place. The prototype's persistence and delivery behavior in a continuous service
remain outside this task. Visual/embedding exploration was not exercised here.

## Reproduce

From this trial directory with Python 3.10+ and the standard library:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 audit/run_audit.py
PYTHONDONTWRITEBYTECODE=1 python3 relay/candidate-frozen/v3/notifier.py
```

The auditor runner writes its new observations under `audit/`; frozen inputs and
candidate files remain intact. Earlier absolute paths in historical records refer
to the original `/private/tmp/via-negativa-interactive-20260928` run. The retained
directory mirrors that layout, and the runner resolves paths relative to itself.
The core skill SHA-256 is recorded in [manifest.json](manifest.json).
