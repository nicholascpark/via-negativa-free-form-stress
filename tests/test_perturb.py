import subprocess
import sys


def test_orchestrate_flag_requires_concern_and_predicates():
    """--orchestrate without --concern-summary and --predicates should error."""
    result = subprocess.run(
        [sys.executable, "perturb.py", "--orchestrate", "--artifact", "test text here"],
        capture_output=True,
        text=True,
        cwd="/Users/nicholaspark/Documents/via-negativa-free-form-stress",
    )
    assert result.returncode != 0
    assert "concern" in result.stderr.lower() or "predicates" in result.stderr.lower()


def test_orchestrate_flag_accepted_with_all_inputs():
    """--orchestrate with all required inputs should not error on flag parsing."""
    result = subprocess.run(
        [
            sys.executable, "perturb.py",
            "--orchestrate",
            "--artifact", "test text for entropy extraction",
            "--concern-summary", "Thinker is planning a career change.",
            "--predicates", "Plans(thinker, career_change)",
            "--stage-b-synthesis", "Pattern: plan is detailed about WHAT.",
        ],
        capture_output=True,
        text=True,
        cwd="/Users/nicholaspark/Documents/via-negativa-free-form-stress",
        timeout=120,
    )
    # May fail on tokenizer load, but should NOT fail on argument parsing
    if result.returncode != 0:
        assert "argument" not in result.stderr.lower()
