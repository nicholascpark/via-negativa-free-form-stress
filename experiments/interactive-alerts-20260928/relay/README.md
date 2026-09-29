# Interaction provenance

Root records each exact practitioner question and simulated-user answer in events.jsonl. Before a question is relayed, root copies the builder workspace into a numbered pre-answer snapshot and records its file hashes. A final candidate snapshot precedes independent artifact evaluation.

setup-frozen preserves public inputs and private user facts/cases committed before the practitioner started. Agents are isolated by fresh contexts and instructed file-access boundaries, not separate operating-system accounts. The root relay can see both sides; the practitioner must not read the private or audit directories.

The supplied harness also requested logging and question/action maps. Observing those records is not evidence that the skill alone caused their creation. These are synthetic role-play interactions, not responses from the real user.
