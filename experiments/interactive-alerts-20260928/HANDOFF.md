# Corrected handoff: synthetic notifier trial

The technician was a **simulated user**, played by an agent using operating facts
fixed before the interaction. Every technician answer and endorsement in this
trial is simulated. This handoff corrects that attribution while preserving the
original candidate and audit records unchanged.

The [offline prototype](relay/candidate-frozen/v3/notifier.py) tracks a fault
episode and the newest source counter separately for each duct. In the supplied
synthetic captures it restores two required pages and removes four repeat/replay
pages relative to the original 20-second cooldown. It prints decisions; it does
not send notifications or operate hardware.

The simulated answers selected independent duct tracking and source-order
filtering. The final answer confirmed existing provisional recovery policies.
The [audit](audit/audit.md) found all 18 scenarios and 72 related transformation
checks passed under that fixed contract. These are results for the frozen
prototype, not evidence from an actual technician or a continuously running bench.

Run from this trial directory using Python 3.10+ and the standard library:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 relay/candidate-frozen/v3/notifier.py
PYTHONDONTWRITEBYTECODE=1 python3 audit/run_audit.py
```

The current skill's question guidance now asks for an unknown operating rule
before inviting agreement with a proposed policy, and keeps separate decisions
out of one bundled confirmation. The [original transcript](TRANSCRIPT.md) remains
historical evidence, including its question-framing weakness. Full production
delivery, persistence and real-user effectiveness remain untested.
