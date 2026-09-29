# Standalone status handoff

An environmental-chamber alert prototype currently pages on every OUT sample.
This offline exercise compares episode-based suppression to that stated baseline.
It is a synthetic conversation: an agent playing the equipment operator supplied
“There is just one chamber for this trial; samples arrive in source order.” No
real operator evidence or chamber measurements were used.

Saved prototype.py compares the baseline with hypothetical one-IN and two-IN
recovery rules. The candidates reduce repeat pages during continuous OUT but
disagree on OUT IN OUT, making the unknown episode-ending rule consequential.
Neither candidate is adopted. MISSING provides no recovery evidence in these
illustrations; hidden recovery during a gap cannot be inferred from the inputs.

Pending question to the simulated operator: “What observation or operating
action tells you that a humidity excursion has ended, so the next OUT should
count as a new episode?” No response has been invented or requested from a human.

checkpoint.md preserves the evidence, exact question, and answer-to-build mapping.
results.txt records local synthetic checks; these validate exercised software
behavior only. Next, encode the operator's ending evidence and replay labeled
trial sequences before adding a real paging connection. No production changes
were made; elapsed work time and compute cost were not measured.
