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


import json
import os
from pathlib import Path

try:
    import transformers
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False

import pytest


@pytest.mark.skipif(not HAS_TRANSFORMERS, reason="transformers not installed")
def test_orchestrate_outputs_valid_manifest():
    result = subprocess.run(
        [
            sys.executable, "perturb.py",
            "--orchestrate",
            "--artifact", "I am planning to leave my engineering role and start consulting.",
            "--concern-summary", "Thinker is planning a career change to consulting.",
            "--predicates", "Plans(thinker, career_change)\nAssumes(plan, network_converts)",
            "--stage-b-synthesis", "Pattern: plan detailed about WHAT, silent about WHO.",
        ],
        capture_output=True, text=True,
        cwd="/Users/nicholaspark/Documents/via-negativa-free-form-stress",
        timeout=120,
    )
    assert result.returncode == 0, f"stderr: {result.stderr}"
    manifest = json.loads(result.stdout)
    assert manifest["protocol"] == "via-negativa-stochastic-perturbation"
    assert manifest["version"] == 1
    assert manifest["round"] == 1
    assert len(manifest["steps"]) == 2
    assert manifest["steps"][0]["step"] == "seed_agents"
    assert manifest["steps"][0]["dispatch"] == "parallel"
    assert manifest["steps"][1]["step"] == "watcher"


@pytest.mark.skipif(not HAS_TRANSFORMERS, reason="transformers not installed")
def test_orchestrate_seed_agents_contain_tokens():
    result = subprocess.run(
        [
            sys.executable, "perturb.py",
            "--orchestrate",
            "--artifact", "Test artifact for token sampling.",
            "--concern-summary", "Test concern.",
            "--predicates", "Test(predicate)",
            "--stage-b-synthesis", "Test synthesis.",
            "--seeds", "2", "--tokens", "3",
        ],
        capture_output=True, text=True,
        cwd="/Users/nicholaspark/Documents/via-negativa-free-form-stress",
        timeout=120,
    )
    manifest = json.loads(result.stdout)
    agents = manifest["steps"][0]["agents"]
    assert len(agents) == 2
    for agent in agents:
        assert "prompt" in agent
        assert "Structural isomorphism" in agent["prompt"]


@pytest.mark.skipif(not HAS_TRANSFORMERS, reason="transformers not installed")
def test_orchestrate_watcher_contains_placeholder():
    result = subprocess.run(
        [
            sys.executable, "perturb.py",
            "--orchestrate",
            "--artifact", "Test artifact.",
            "--concern-summary", "Test.",
            "--predicates", "X(y)",
            "--stage-b-synthesis", "Test synthesis.",
        ],
        capture_output=True, text=True,
        cwd="/Users/nicholaspark/Documents/via-negativa-free-form-stress",
        timeout=120,
    )
    manifest = json.loads(result.stdout)
    watcher = manifest["steps"][1]
    assert "{{SEED_AGENT_RESULTS}}" in watcher["prompt"]
    assert watcher["stage_b_synthesis"] == "Test synthesis."


@pytest.mark.skipif(not HAS_TRANSFORMERS, reason="transformers not installed")
def test_orchestrate_iteration_block():
    result = subprocess.run(
        [
            sys.executable, "perturb.py",
            "--orchestrate",
            "--artifact", "Test artifact.",
            "--concern-summary", "Test.",
            "--predicates", "X(y)",
            "--stage-b-synthesis", "Test.",
        ],
        capture_output=True, text=True,
        cwd="/Users/nicholaspark/Documents/via-negativa-free-form-stress",
        timeout=120,
    )
    manifest = json.loads(result.stdout)
    iteration = manifest["iteration"]
    assert iteration["signal_threshold"] == 0.5
    assert iteration["max_rounds"] == 3
    assert "--round 2" in iteration["next_round_command"]
