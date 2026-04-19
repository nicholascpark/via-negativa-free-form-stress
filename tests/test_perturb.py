import subprocess
import sys

from perturb import (
    build_manifest,
    extract_anchor_terms,
    generate_seeds,
    resolve_displacement_mode,
    sample_tokens,
)


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


def test_generate_seeds_supports_more_than_four_outputs():
    seeds = generate_seeds("artifact text for deterministic seed expansion", 6, round_num=1)
    assert len(seeds) == 6
    assert len(set(seeds)) == 6


def test_generate_seeds_change_across_rounds():
    artifact = "I want to leave my job and start something of my own."
    round_one = generate_seeds(artifact, 3, round_num=1)
    round_two = generate_seeds(artifact, 3, round_num=2)
    assert round_one != round_two


def test_extract_anchor_terms_prefers_content_words():
    anchors = extract_anchor_terms(
        "Consulting consulting identity transition planning planning planning family."
    )
    assert "planning" in anchors
    assert "consulting" in anchors


def test_sample_tokens_prefers_non_dominant_scripts():
    token_catalog = [
        {"id": 1, "text": "alpha", "script": "latin", "length": 5},
        {"id": 2, "text": "beta", "script": "latin", "length": 4},
        {"id": 3, "text": "риб", "script": "cyrillic", "length": 3},
        {"id": 4, "text": "وحد", "script": "arabic", "length": 3},
        {"id": 5, "text": "클럽", "script": "hangul", "length": 2},
        {"id": 6, "text": "河川", "script": "cjk", "length": 2},
    ]
    sampled = sample_tokens(
        token_catalog,
        seeds=[1234],
        k=4,
        anchor_terms=["consulting", "identity"],
        dominant_scripts=["latin"],
    )
    scripts = sampled["seed_1"]["scripts"]
    assert any(script != "latin" for script in scripts)
    assert len(set(scripts)) >= 3


def test_sample_tokens_accepts_embedding_scores():
    class FakeEmbeddingScorer:
        def similarity_to_anchors(self, candidates, anchors):
            del anchors
            return {
                candidate: {
                    "alpha": 0.95,
                    "beta": 0.9,
                    "rift": 0.2,
                    "void": 0.1,
                }[candidate]
                for candidate in candidates
            }

    token_catalog = [
        {"id": 1, "text": "alpha", "script": "latin", "length": 5},
        {"id": 2, "text": "beta", "script": "latin", "length": 4},
        {"id": 3, "text": "rift", "script": "latin", "length": 4},
        {"id": 4, "text": "void", "script": "latin", "length": 4},
    ]
    sampled = sample_tokens(
        token_catalog,
        seeds=[7],
        k=2,
        anchor_terms=["identity", "consulting"],
        dominant_scripts=["latin"],
        displacement_mode="embedding",
        embedding_scorer=FakeEmbeddingScorer(),
    )
    assert sampled["seed_1"]["tokens"] == ["void", "rift"]


def test_resolve_displacement_mode_lexical_short_circuits():
    actual_mode, scorer, note = resolve_displacement_mode(
        displacement_mode="lexical",
        embedding_model="irrelevant-model",
    )
    assert actual_mode == "lexical"
    assert scorer is None
    assert "lexical" in note


def test_build_manifest_includes_sampler_metadata_and_new_input_fields():
    manifest = build_manifest(
        seed_packets={
            "seed_1": {"tokens": ["foo", "bar"], "scripts": ["latin", "arabic"]},
        },
        concern="Thinker is planning a transition.",
        predicates="Plans(thinker, transition)",
        stage_b="Pattern: the plan is operationally rich and identity-poor.",
        round_num=1,
        script_path="${CLAUDE_SKILL_DIR}/perturb.py",
        sampler_context={
            "round_strategy": "negative_lexicon",
            "round_description": "Push away from default phrasing.",
            "artifact_anchor_terms": ["identity", "consulting"],
            "artifact_dominant_scripts": ["latin"],
            "artifact_fingerprint": {
                "normalized_sha256": "abc123",
                "char_count": 42,
                "word_count": 7,
                "sentence_count": 2,
                "unique_word_ratio": 0.8,
            },
            "selection_strategy": "cross-script low-overlap sampling",
            "displacement_mode": "hybrid",
            "embedding_model": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            "displacement_note": "hybrid displacement using sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            "round": 1,
        },
    )
    assert manifest["version"] == 3
    assert manifest["schema"]["seed_agent_result_format"] == "json"
    assert "bridge_schema.py watcher-payload" in manifest["schema"]["watcher_payload_builder_command"]
    assert "bridge_schema.py watcher-prompt" in manifest["schema"]["watcher_prompt_builder_command"]
    assert manifest["sampler"]["round_strategy"] == "negative_lexicon"
    assert manifest["steps"][1]["input_fields"] == [
        "bridge_type",
        "bridge_predicates",
        "counterevidence",
        "reflection",
        "signal",
    ]


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
    assert manifest["version"] == 3
    assert manifest["round"] == 1
    assert len(manifest["steps"]) == 2
    assert manifest["steps"][0]["step"] == "seed_agents"
    assert manifest["steps"][0]["dispatch"] == "parallel"
    assert manifest["steps"][1]["step"] == "watcher"
    assert manifest["sampler"]["round_strategy"]
    assert manifest["schema"]["seed_result_delimiter"] == "===SEED_RESULT==="
    assert "watcher-prompt" in manifest["schema"]["watcher_prompt_builder_command"]


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
        assert "counterevidence" in agent["prompt"]
        assert "valid JSON" in agent["prompt"]


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
    assert "counterevidence" in watcher["prompt"]
    assert manifest["schema"]["watcher_payload_format"] == "json-array"


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


@pytest.mark.skipif(not HAS_TRANSFORMERS, reason="transformers not installed")
def test_orchestrate_persists_inputs_to_tmp():
    """First --orchestrate call should write inputs to /tmp/vn-*.txt."""
    for f in ["/tmp/vn-artifact.txt", "/tmp/vn-concern.txt",
              "/tmp/vn-predicates.txt", "/tmp/vn-stageb.txt"]:
        if os.path.exists(f):
            os.remove(f)

    result = subprocess.run(
        [
            sys.executable, "perturb.py",
            "--orchestrate",
            "--artifact", "Persist test artifact.",
            "--concern-summary", "Persist test concern.",
            "--predicates", "Persist(test)",
            "--stage-b-synthesis", "Persist test synthesis.",
        ],
        capture_output=True, text=True,
        cwd="/Users/nicholaspark/Documents/via-negativa-free-form-stress",
        timeout=120,
    )
    assert result.returncode == 0
    assert os.path.exists("/tmp/vn-artifact.txt")
    assert os.path.exists("/tmp/vn-concern.txt")
    assert os.path.exists("/tmp/vn-predicates.txt")
    assert os.path.exists("/tmp/vn-stageb.txt")
    assert Path("/tmp/vn-artifact.txt").read_text() == "Persist test artifact."
    assert Path("/tmp/vn-predicates.txt").read_text() == "Persist(test)"


@pytest.mark.skipif(not HAS_TRANSFORMERS, reason="transformers not installed")
def test_orchestrate_with_file_flags():
    """--orchestrate should work with file flags for iteration rounds."""
    Path("/tmp/vn-test-artifact.txt").write_text("File flag test artifact.")
    Path("/tmp/vn-test-concern.txt").write_text("File flag test concern.")
    Path("/tmp/vn-test-predicates.txt").write_text("FileTest(predicate)")
    Path("/tmp/vn-test-stageb.txt").write_text("File flag test synthesis.")

    result = subprocess.run(
        [
            sys.executable, "perturb.py",
            "--orchestrate",
            "--artifact-file", "/tmp/vn-test-artifact.txt",
            "--concern-file", "/tmp/vn-test-concern.txt",
            "--predicates-file", "/tmp/vn-test-predicates.txt",
            "--stage-b-file", "/tmp/vn-test-stageb.txt",
            "--round", "2",
        ],
        capture_output=True, text=True,
        cwd="/Users/nicholaspark/Documents/via-negativa-free-form-stress",
        timeout=120,
    )
    assert result.returncode == 0, f"stderr: {result.stderr}"
    manifest = json.loads(result.stdout)
    assert manifest["round"] == 2
    assert "--round 3" in manifest["iteration"]["next_round_command"]
    assert "FileTest(predicate)" in manifest["steps"][0]["agents"][0]["prompt"]
