import base64
import json
import subprocess
import sys

import pytest

from bridge_schema import (
    build_completed_watcher_prompt,
    BridgeSchemaError,
    compile_watcher_payload,
    normalize_seed_agent_result,
    parse_seed_result_batch,
    SeedAgentResult,
    parse_seed_agent_result,
    render_watcher_payload,
)


def test_parse_seed_agent_result_accepts_valid_json():
    raw = json.dumps({
        "story": "A raft drifts through a mirrored river while a planner watches the shoreline recede.",
        "story_predicates": ["BuiltFor(raft, crossing)", "NatureOf(river, reflecting)"],
        "bridge_type": "structural_isomorphism",
        "bridge_predicates": ["BuiltFor(plan, transition)", "NatureOf(consulting, reflecting)"],
        "counterevidence": "If consulting mainly transports existing expertise without reflecting identity back, the bridge collapses.",
        "reflection": "The bridge suggests the plan is not only about movement but about what the medium reveals back to the thinker.",
        "signal": 4,
    })
    result = parse_seed_agent_result(raw)
    assert isinstance(result, SeedAgentResult)
    assert result.bridge_type == "structural_isomorphism"
    assert len(result.bridge_predicates) == 2


def test_parse_seed_agent_result_accepts_fenced_json():
    raw = """```json
{
  "story": "A long corridor of names bends back on itself while a traveler counts echoes.",
  "story_predicates": ["Counts(traveler, echoes)"],
  "bridge_type": "negation_revelation",
  "bridge_predicates": ["NOTPortable(identity_across_media)"],
  "counterevidence": "If identity transfers intact across contexts, the claimed negation is just decorative.",
  "reflection": "The echo-counting image suggests the thinker is assuming continuity where the medium may actually disrupt it.",
  "signal": 3
}
```"""
    result = parse_seed_agent_result(raw)
    assert result.bridge_type == "negation_revelation"


def test_parse_seed_agent_result_rejects_missing_fields():
    raw = json.dumps({
        "story": "Too short to matter, but still present enough for parsing tests.",
        "bridge_type": "none",
        "bridge_predicates": [],
        "counterevidence": "Any real bridge would be redundant with Stage B.",
        "reflection": "This should fail because required fields are missing from the payload.",
        "signal": 0,
    })
    with pytest.raises(BridgeSchemaError):
        parse_seed_agent_result(raw)


def test_parse_seed_agent_result_rejects_none_bridge_with_predicates():
    raw = json.dumps({
        "story": "A corridor loops in silence while someone pretends the exit is obvious.",
        "story_predicates": ["Loops(corridor)"],
        "bridge_type": "none",
        "bridge_predicates": ["Actually(there_is_a_bridge)"],
        "counterevidence": "If a bridge is really present, this should not be typed as none.",
        "reflection": "The result claims no bridge but still smuggles one in.",
        "signal": 1,
    })
    with pytest.raises(BridgeSchemaError):
        parse_seed_agent_result(raw)


def test_render_watcher_payload_drops_story_fields():
    results = [
        SeedAgentResult(
            story="A valid story about threshold crossings and reflected names.",
            story_predicates=["Crosses(traveler, threshold)"],
            bridge_type="compositional_insight",
            bridge_predicates=["DebtTo(thinker, imagined_self)"],
            counterevidence="If the imagined self adds no obligations, the derived debt predicate is overstated.",
            reflection="The story implies the thinker may be managing an obligation to a future self they have not authorized.",
            signal=4,
        )
    ]
    payload = json.loads(render_watcher_payload(results))
    assert list(payload[0].keys()) == [
        "bridge_type",
        "bridge_predicates",
        "counterevidence",
        "reflection",
        "signal",
    ]


def test_build_completed_watcher_prompt_replaces_placeholder():
    prompt = "Watcher header\n{{SEED_AGENT_RESULTS}}\nWatcher footer"
    payload = '[{"bridge_type":"none","bridge_predicates":[],"counterevidence":"x","reflection":"y","signal":1}]'
    completed = build_completed_watcher_prompt(prompt, payload)
    assert "{{SEED_AGENT_RESULTS}}" not in completed
    assert payload in completed


def test_parse_seed_result_batch_accepts_json_array():
    raw = json.dumps([
        {
            "story": "A raft drifts through a mirrored river while a planner watches the shoreline recede.",
            "story_predicates": ["BuiltFor(raft, crossing)"],
            "bridge_type": "structural_isomorphism",
            "bridge_predicates": ["BuiltFor(plan, transition)"],
            "counterevidence": "If the medium does not actually reflect identity back, the bridge fails.",
            "reflection": "The result suggests a plan may expose the thinker rather than simply transport them.",
            "signal": 4,
        }
    ])
    entries = parse_seed_result_batch(raw)
    assert isinstance(entries, list)
    assert entries[0]["bridge_type"] == "structural_isomorphism"


def test_parse_seed_result_batch_accepts_delimited_blocks():
    raw = """
===SEED_RESULT===
{"story":"A raft drifts through a mirrored river while a planner watches the shoreline recede.","story_predicates":["BuiltFor(raft, crossing)"],"bridge_type":"structural_isomorphism","bridge_predicates":["BuiltFor(plan, transition)"],"counterevidence":"If the medium does not actually reflect identity back, the bridge fails.","reflection":"The result suggests a plan may expose the thinker rather than simply transport them.","signal":4}
===SEED_RESULT===
{"story":"A corridor loops in silence while someone counts names and forgets the door they entered.","story_predicates":["Counts(traveler, names)"],"bridge_type":"none","bridge_predicates":[],"counterevidence":"If a stable structural bridge exists, calling this none is wrong.","reflection":"This result concludes that the story failed to produce a defensible bridge.","signal":1}
"""
    entries = parse_seed_result_batch(raw)
    assert len(entries) == 2
    assert entries[0].startswith("{")


def test_compile_watcher_payload_drops_invalid_entries_in_non_strict_mode():
    payload, errors, valid_results = compile_watcher_payload([
        {
            "story": "A raft drifts through a mirrored river while a planner watches the shoreline recede.",
            "story_predicates": ["BuiltFor(raft, crossing)"],
            "bridge_type": "structural_isomorphism",
            "bridge_predicates": ["BuiltFor(plan, transition)"],
            "counterevidence": "If the medium does not actually reflect identity back, the bridge fails.",
            "reflection": "The result suggests a plan may expose the thinker rather than simply transport them.",
            "signal": 4,
        },
        {
            "story": "invalid",
            "story_predicates": [],
            "bridge_type": "none",
            "bridge_predicates": [],
            "counterevidence": "Too short.",
            "reflection": "Also too short.",
            "signal": 0,
        },
    ])
    watcher_payload = json.loads(payload)
    assert len(valid_results) == 1
    assert len(watcher_payload) == 1
    assert errors


def test_compile_watcher_payload_rejects_all_invalid_entries():
    with pytest.raises(BridgeSchemaError):
        compile_watcher_payload([
            {
                "story": "invalid",
                "story_predicates": [],
                "bridge_type": "none",
                "bridge_predicates": [],
                "counterevidence": "Too short.",
                "reflection": "Also too short.",
                "signal": 0,
            }
        ])


def test_normalize_seed_agent_result_accepts_decoded_json_object():
    entry = {
        "story": "A raft drifts through a mirrored river while a planner watches the shoreline recede.",
        "story_predicates": ["BuiltFor(raft, crossing)"],
        "bridge_type": "structural_isomorphism",
        "bridge_predicates": ["BuiltFor(plan, transition)"],
        "counterevidence": "If the medium does not actually reflect identity back, the bridge fails.",
        "reflection": "The result suggests a plan may expose the thinker rather than simply transport them.",
        "signal": 4,
    }
    result = normalize_seed_agent_result(entry)
    assert result.bridge_type == "structural_isomorphism"


def test_bridge_schema_cli_validate_outputs_normalized_json():
    raw = json.dumps({
        "story": "A raft drifts through a mirrored river while a planner watches the shoreline recede.",
        "story_predicates": ["BuiltFor(raft, crossing)"],
        "bridge_type": "structural_isomorphism",
        "bridge_predicates": ["BuiltFor(plan, transition)"],
        "counterevidence": "If the medium does not actually reflect identity back, the bridge fails.",
        "reflection": "The result suggests a plan may expose the thinker rather than simply transport them.",
        "signal": 4,
    })
    result = subprocess.run(
        [sys.executable, "bridge_schema.py", "validate"],
        input=raw,
        capture_output=True,
        text=True,
        cwd="/Users/nicholaspark/Documents/via-negativa-free-form-stress",
        check=False,
    )
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["bridge_type"] == "structural_isomorphism"


def test_bridge_schema_cli_watcher_payload_accepts_delimited_stdin():
    raw = """
===SEED_RESULT===
{"story":"A raft drifts through a mirrored river while a planner watches the shoreline recede.","story_predicates":["BuiltFor(raft, crossing)"],"bridge_type":"structural_isomorphism","bridge_predicates":["BuiltFor(plan, transition)"],"counterevidence":"If the medium does not actually reflect identity back, the bridge fails.","reflection":"The result suggests a plan may expose the thinker rather than simply transport them.","signal":4}
===SEED_RESULT===
{"story":"A corridor loops in silence while someone counts names and forgets the door they entered.","story_predicates":["Counts(traveler, names)"],"bridge_type":"none","bridge_predicates":[],"counterevidence":"If a stable structural bridge exists, calling this none is wrong.","reflection":"This result concludes that the story failed to produce a defensible bridge.","signal":1}
"""
    result = subprocess.run(
        [sys.executable, "bridge_schema.py", "watcher-payload"],
        input=raw,
        capture_output=True,
        text=True,
        cwd="/Users/nicholaspark/Documents/via-negativa-free-form-stress",
        check=False,
    )
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert len(payload) == 2
    assert payload[0]["bridge_type"] == "structural_isomorphism"
    assert "Accepted 2 of 2" in result.stderr


def test_bridge_schema_cli_watcher_payload_returns_error_if_none_valid():
    raw = """
===SEED_RESULT===
{"story":"short","story_predicates":[],"bridge_type":"none","bridge_predicates":[],"counterevidence":"short","reflection":"short","signal":0}
"""
    result = subprocess.run(
        [sys.executable, "bridge_schema.py", "watcher-payload"],
        input=raw,
        capture_output=True,
        text=True,
        cwd="/Users/nicholaspark/Documents/via-negativa-free-form-stress",
        check=False,
    )
    assert result.returncode != 0
    assert "No valid seed-agent results" in result.stderr


def test_bridge_schema_cli_watcher_prompt_outputs_completed_prompt():
    prompt = "Watcher start\n{{SEED_AGENT_RESULTS}}\nWatcher end"
    prompt_b64 = base64.b64encode(prompt.encode("utf-8")).decode("ascii")
    raw = """
===SEED_RESULT===
{"story":"A raft drifts through a mirrored river while a planner watches the shoreline recede.","story_predicates":["BuiltFor(raft, crossing)"],"bridge_type":"structural_isomorphism","bridge_predicates":["BuiltFor(plan, transition)"],"counterevidence":"If the medium does not actually reflect identity back, the bridge fails.","reflection":"The result suggests a plan may expose the thinker rather than simply transport them through change.","signal":4}
"""
    result = subprocess.run(
        [sys.executable, "bridge_schema.py", "watcher-prompt", "--prompt-b64", prompt_b64],
        input=raw,
        capture_output=True,
        text=True,
        cwd="/Users/nicholaspark/Documents/via-negativa-free-form-stress",
        check=False,
    )
    assert result.returncode == 0
    assert "{{SEED_AGENT_RESULTS}}" not in result.stdout
    assert '"bridge_type": "structural_isomorphism"' in result.stdout
    assert "Watcher start" in result.stdout
