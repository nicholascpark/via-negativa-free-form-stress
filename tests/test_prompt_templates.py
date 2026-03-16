from prompt_templates import render_seed_agent_prompt


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
    assert "story" in result
    assert "story_predicates" in result
    assert "bridge_predicates" in result
    assert "reflection" in result
    assert "signal" in result
