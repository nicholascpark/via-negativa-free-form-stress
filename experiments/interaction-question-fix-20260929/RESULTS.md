# Focused post-fix exercise — 2026-09-29

A new agent with no conversation-history fork used the revised skill on a synthetic
single-chamber humidity notifier. The public request described repeated OUT
warnings and a need to notice new episodes; the only supplied operator answer
was that there was one chamber and readings arrived in source order. The operator
was explicitly an agent role. The exercise requested one question checkpoint and
a standalone handoff, with no actual user contact or invented answer.

The agent asked:

> What observation or operating action tells you that a humidity excursion has ended, so the next OUT should count as a new episode?

The [checkpoint](checkpoint.md) preserves alternative answer-to-action mappings.
The [handoff](handoff.md) explicitly identifies the operator as agent-played and
states that no real operator evidence was used. Competing recovery rules remain
provisional. These outputs address the earlier bundled-confirmation and speaker-
provenance findings in this focused exercise.

The [prototype](prototype.py) passed six synthetic cases and 2,186 short-trace
contract checks; those are development checks of the hypothetical implementations,
not evidence for a correct physical recovery rule. Run `python3 prototype.py`
from this directory. The question has not been answered, so this is not a repeat
of the full interactive trial and does not establish real-human framing neutrality.

Skill SHA-256: `529ddd9db07910078bec89691ddd94e1ff95b84c15725bbadd0fa413c56380e3`.

The original interactive trial remains frozen under its earlier skill hash.
