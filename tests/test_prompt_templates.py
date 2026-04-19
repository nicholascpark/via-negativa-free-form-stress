from prompt_templates import render_seed_agent_prompt
from prompt_templates import render_watcher_prompt


def test_seed_agent_prompt_contains_tokens():
    tokens = ["Esituluilo", "риб", "وحد"]
    concern = "Thinker is planning a career change to consulting."
    predicates = "Plans(thinker, career_change)\nAssumes(plan, network_converts)"
    result = render_seed_agent_prompt(tokens, concern, predicates)
    for token in tokens:
        assert token in result


def test_seed_agent_prompt_contains_predicates():
    tokens = ["foo", "bar"]
    concern = "Test concern."
    predicates = "Plans(thinker, X)\nAbsent(plan, Y)"
    result = render_seed_agent_prompt(tokens, concern, predicates)
    assert "Plans(thinker, X)" in result
    assert "Absent(plan, Y)" in result


def test_seed_agent_prompt_contains_concern_summary():
    tokens = ["foo"]
    concern = "Thinker is stuck on a decision about moving cities."
    predicates = "Plans(thinker, X)"
    result = render_seed_agent_prompt(tokens, concern, predicates)
    assert "moving cities" in result


def test_seed_agent_prompt_contains_bridge_types():
    tokens = ["foo"]
    concern = "Test."
    predicates = "X(y)"
    result = render_seed_agent_prompt(tokens, concern, predicates)
    assert "Structural isomorphism" in result
    assert "Negation revelation" in result
    assert "Compositional insight" in result


def test_seed_agent_prompt_contains_output_format():
    tokens = ["foo"]
    concern = "Test."
    predicates = "X(y)"
    result = render_seed_agent_prompt(tokens, concern, predicates)
    assert '"story"' in result
    assert '"story_predicates"' in result
    assert '"bridge_type"' in result
    assert '"bridge_predicates"' in result
    assert '"counterevidence"' in result
    assert '"reflection"' in result
    assert '"signal"' in result
    assert "valid JSON" in result


def test_seed_agent_prompt_contains_anchor_terms_and_profile():
    tokens = ["foo"]
    concern = "Test."
    predicates = "X(y)"
    result = render_seed_agent_prompt(
        tokens,
        concern,
        predicates,
        artifact_anchors=["identity", "consulting"],
        perturbation_profile={
            "round_strategy": "negative_lexicon",
            "round_description": "Push away from default phrasing.",
            "artifact_dominant_scripts": ["latin"],
            "sampled_scripts": ["arabic", "cyrillic"],
            "displacement_mode": "hybrid",
            "displacement_note": "hybrid displacement using a multilingual encoder",
            "selection_strategy": "cross-script low-overlap sampling",
        },
    )
    assert "identity" in result
    assert "negative_lexicon" in result
    assert "hybrid" in result
    assert "cross-script low-overlap sampling" in result


def test_watcher_prompt_contains_scoring_formula():
    stage_b = "Pattern: plan is detailed about WHAT, silent about WHO."
    result = render_watcher_prompt(stage_b)
    assert "0.3*Specificity" in result or "0.3 * Specificity" in result
    assert "0.3*Novelty" in result or "0.3 * Novelty" in result
    assert "0.2*FormalValidity" in result or "0.2 * FormalValidity" in result
    assert "0.2*Actionability" in result or "0.2 * Actionability" in result


def test_watcher_prompt_contains_thresholds():
    stage_b = "Test synthesis."
    result = render_watcher_prompt(stage_b)
    assert "0.3" in result
    assert "0.5" in result
    assert "0.7" in result


def test_watcher_prompt_contains_stage_b_for_novelty():
    stage_b = "The latent thought is about identity transformation."
    result = render_watcher_prompt(stage_b)
    assert "identity transformation" in result


def test_watcher_prompt_contains_placeholder():
    stage_b = "Test."
    result = render_watcher_prompt(stage_b)
    assert "{{SEED_AGENT_RESULTS}}" in result
    assert "JSON array" in result


def test_watcher_prompt_contains_forced_connection_check():
    stage_b = "Test."
    result = render_watcher_prompt(stage_b)
    assert "Forced Connection" in result
    assert "counterevidence" in result


def test_watcher_prompt_contains_meta_assessment():
    stage_b = "Test."
    result = render_watcher_prompt(stage_b)
    assert "Stage B" in result
    assert "deterministic" in result.lower()


def test_watcher_prompt_contains_bridge_type_check():
    stage_b = "Test."
    result = render_watcher_prompt(stage_b)
    assert "Bridge type" in result
