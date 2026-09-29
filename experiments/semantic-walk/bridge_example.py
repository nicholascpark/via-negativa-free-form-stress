#!/usr/bin/env python3
"""Synthetic finite predicate search; not a discovery or a performance study."""
import itertools
import json


FIELDS = ("tenant", "sku", "locale")
CONTRACT = {
    "source": "Separately declared fictional task contract for this illustration",
    "response_identity": list(FIELDS),
    "sharing_permission": "Only requests with equal tenant, sku, and locale may share production.",
    "positive_requirement": "Two distinct request instances with identical identity may share production.",
    "freshness": "Returned data must be no more than one second old.",
}


def contract_permission(left, right):
    # Independent oracle: explicit contract clauses, not the searched key list.
    return (left["tenant"] == right["tenant"]
            and left["sku"] == right["sku"]
            and left["locale"] == right["locale"])


def predicate(keys, left, right):
    return all(left[field] == right[field] for field in keys)


def generate():
    domain = {"tenant": ["tenant-a", "tenant-b"], "sku": ["sku-1", "sku-2"],
              "locale": ["en", "fr"]}
    requests = []
    for values in itertools.product(*(domain[field] for field in FIELDS)):
        for _ in range(2):
            requests.append({"instance": f"request-{len(requests) + 1:02d}",
                             **dict(zip(FIELDS, values))})
    pairs = list(itertools.combinations(requests, 2))
    grammar = [keys for size in range(4) for keys in itertools.combinations(FIELDS, size)]
    candidates = []
    admissible = []
    for keys in grammar:
        unsafe = [(a, b) for a, b in pairs if predicate(keys, a, b) and not contract_permission(a, b)]
        missed = [(a, b) for a, b in pairs if contract_permission(a, b) and not predicate(keys, a, b)]
        accepted = not unsafe and not missed
        if accepted:
            admissible.append(keys)
        candidates.append({"fields": list(keys), "status": "accepted" if accepted else "rejected",
                           "unsafe_sharing_pairs": len(unsafe), "missed_duplicate_pairs": len(missed),
                           "counterexample": {"requests": list(unsafe[0]), "expected_share": False}
                           if unsafe else None})
    chosen = min(admissible, key=lambda keys: (len(keys), keys))
    proposal_keys = {"sku_only": ("sku",), "full_identity": FIELDS}
    disagreements = [(a, b) for a, b in pairs
                     if predicate(("sku",), a, b) != predicate(FIELDS, a, b)]
    cases = []

    def add_case(role, pair, distinguishes):
        a, b = pair
        expected = contract_permission(a, b)
        outputs = {name: predicate(keys, a, b) for name, keys in proposal_keys.items()}
        cases.append({"id": f"case-{len(cases) + 1}", "role": role,
                      "requests": [a, b], "expected_share": expected,
                      "expectation_source": "declared_contract.sharing_permission / positive_requirement",
                      "distinguishes_proposals": distinguishes, "observed": outputs,
                      "validation": {name: "pass" if actual == expected else "fail"
                                     for name, actual in outputs.items()}})

    # Discover disagreements first; retain one boundary per differing field.
    for field in FIELDS:
        boundary = [(a, b) for a, b in disagreements
                    if [f for f in FIELDS if a[f] != b[f]] == [field]]
        if boundary:
            add_case(f"discriminating boundary: {field}", boundary[0], True)
    duplicate = next(pair for pair in pairs if contract_permission(*pair))
    add_case("positive duplicate: coalescing remains possible", duplicate, False)
    preserved = next(pair for pair in pairs
                     if [f for f in FIELDS if pair[0][f] != pair[1][f]] == ["sku"])
    add_case("shared boundary: different product", preserved, False)
    cases.append({"id": "case-5", "role": "freshness requirement outside this model",
                  "situation": "Identical requests encounter a response older than one second.",
                  "expected_behavior": "Do not return stale data as satisfying the freshness contract.",
                  "expectation_source": "declared_contract.freshness", "validation": "pending",
                  "reason": "No clocks, production, cache, or execution model is present."})
    checks = {
        "eight_predicates_enumerated": len(grammar) == 8,
        "sixteen_instances_and_120_pairs": len(requests) == 16 and len(pairs) == 120,
        "eight_positive_duplicate_pairs": sum(contract_permission(*pair) for pair in pairs) == 8,
        "chosen_is_only_admissible_predicate": admissible == [FIELDS],
        "chosen_agrees_with_contract_on_all_pairs": all(predicate(chosen, *p) == contract_permission(*p) for p in pairs),
        "discriminating_cases_expose_sku_only_errors": all(
            c["validation"] == {"sku_only": "fail", "full_identity": "pass"}
            for c in cases if c.get("distinguishes_proposals")),
        "both_missing_identity_dimensions_exposed": {c["role"].split(": ")[-1] for c in cases
                                                      if c.get("distinguishes_proposals")} == {"tenant", "locale"},
    }
    if not all(checks.values()):
        raise AssertionError(checks)
    return {
        "status": "synthetic_illustration", "discovered_from_cue_walk": False,
        "source_mechanism": "Multiple equivalent consumers share one production step.",
        "target": "Coalesce fictional product requests using a searched equivalence predicate.",
        "declared_contract": CONTRACT, "grammar": "P_K(a,b) = all(a[f] == b[f] for f in K); K subset of {tenant,sku,locale}",
        "domain_bounds": {"values": domain, "instances_per_identity": 2, "request_instances": 16,
                          "unordered_distinct_instance_pairs": len(pairs)},
        "candidate_predicates": candidates, "chosen_predicate": {"fields": list(chosen),
            "selection": "Minimum field count satisfying all finite safety and positive-duplicate constraints."},
        "proposal_disagreement_count": len(disagreements), "generated_cases": cases,
        "self_checks": checks, "measured_performance": None,
        "limits": ["Finite enumeration establishes only agreement on the declared domain and grammar.",
                   "Generated cases are development checks, not independent evidence of method effectiveness.",
                   "Timing, freshness execution, cancellation, failure, and production effects remain unmodeled.",
                   "No useful outcome for a real user or latency improvement has been demonstrated."],
    }


if __name__ == "__main__":
    print(json.dumps(generate(), indent=2, ensure_ascii=False, allow_nan=False))
