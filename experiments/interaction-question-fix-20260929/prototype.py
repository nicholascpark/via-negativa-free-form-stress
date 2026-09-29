"""Offline v0 probe; candidate recovery rules are hypotheses, not adopted policy."""
from itertools import product
import json

SYMBOLS = ("OUT", "IN", "MISSING")


def pages(samples, recovery_count=None):
    """Return one-based page positions. None models the stated original script.

    Candidate rules: after recovery_count consecutive INs, end the episode.
    MISSING breaks the recovery streak but cannot itself end an episode.
    Initial OUT pages. This is a fresh trial, with no restart semantics.
    """
    active = False
    streak = 0
    emitted = []
    for position, symbol in enumerate(samples, 1):
        if symbol not in SYMBOLS:
            raise ValueError(symbol)
        if symbol == "OUT":
            if recovery_count is None or not active:
                emitted.append(position)
            active = True
            streak = 0
        elif symbol == "IN":
            streak += 1
            if recovery_count is not None and streak >= recovery_count:
                active = False
        else:
            streak = 0
    return emitted


if __name__ == "__main__":
    # Predictions frozen with this version before execution. Synthetic inputs.
    cases = [
        ("OUT OUT OUT", [[1, 2, 3], [1], [1]]),
        ("OUT IN OUT", [[1, 3], [1, 3], [1]]),
        ("OUT IN IN OUT", [[1, 4], [1, 4], [1, 4]]),
        ("OUT MISSING OUT", [[1, 3], [1], [1]]),
        ("OUT IN MISSING IN OUT", [[1, 5], [1, 5], [1]]),
        ("MISSING IN OUT", [[3], [3], [3]]),
    ]
    print("Synthetic development cases; page positions are one-based.")
    print("Columns: stated original, hypothetical one-IN recovery, hypothetical two-IN recovery")
    for raw, expected in cases:
        actual = [pages(raw.split(), n) for n in (None, 1, 2)]
        assert actual == expected, (raw, expected, actual)
        print(json.dumps({"input": raw, "expected": expected, "actual": actual}))
    # Check each candidate's software contract, not whether it matches the chamber.
    checked = 0
    for length in range(7):
        for samples in product(SYMBOLS, repeat=length):
            for n in (1, 2):
                emitted = pages(samples, n)
                assert all(samples[i - 1] == "OUT" for i in emitted)
                if "OUT" in samples:
                    assert emitted[0] == samples.index("OUT") + 1
                for left, right in zip(emitted, emitted[1:]):
                    between = samples[left:right - 1]
                    assert any(between[i:i + n] == ("IN",) * n
                               for i in range(len(between) - n + 1))
                checked += 1
    print(f"PASS: 6 frozen cases and {checked} candidate-trace contract checks (length 0–6).")
