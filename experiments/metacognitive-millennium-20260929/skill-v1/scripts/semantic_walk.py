#!/usr/bin/env python3
"""Sample reproducible cue walks from supplied, shared-space embeddings.

This controller measures geometry and samples cues. It does not create embeddings,
interpret images, assess utility, or run a language model. All vectors must come
from the encoder and revision named in the input.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import random
import sys
from typing import Any


BANDS = ("near", "middle", "far")
DEFAULT_WEIGHTS = (0.2, 0.5, 0.3)


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a nonempty string")
    return value


def _integer(value: Any, field: str, minimum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f"{field} must be an integer >= {minimum}")
    return value


def normalize_embedding(vector: Any, dimension: int | None = None) -> list[float]:
    """Normalize finite, nonzero vectors without squaring enormous values."""
    if not isinstance(vector, (list, tuple)) or not vector:
        raise ValueError("embedding must be a nonempty numeric array")
    if dimension is not None and len(vector) != dimension:
        raise ValueError(f"embedding dimension {len(vector)} != declared {dimension}")
    if any(isinstance(x, bool) or not isinstance(x, (int, float)) for x in vector):
        raise ValueError("embedding entries must be numbers, not booleans")
    try:
        values = [float(x) for x in vector]
    except (OverflowError, ValueError) as exc:
        raise ValueError("embedding entries must be finite") from exc
    if not all(math.isfinite(x) for x in values):
        raise ValueError("embedding entries must be finite")
    scale = max(abs(x) for x in values)
    if scale == 0:
        raise ValueError("embedding must not be the zero vector")
    scaled = [x / scale for x in values]
    norm = math.sqrt(math.fsum(x * x for x in scaled))
    return [x / norm for x in scaled]


def cosine_distance(left: Any, right: Any) -> float:
    """Return 1 - cosine similarity, in [0, 2]; inputs need not be normalized."""
    a = normalize_embedding(left)
    b = normalize_embedding(right, len(a))
    dot = math.fsum(x * y for x, y in zip(a, b))
    return 1.0 - max(-1.0, min(1.0, dot))


def validate_input(payload: Any) -> dict[str, Any]:
    """Validate provenance declarations and return a normalized copy.

    A global encoder declaration is mandatory. Optional declarations on individual
    items must exactly match it; absent declarations inherit it. Metadata cannot
    verify that vectors genuinely came from their claimed encoder.
    """
    if not isinstance(payload, dict):
        raise ValueError("input must be a JSON object")
    encoder = payload.get("encoder")
    if not isinstance(encoder, dict):
        raise ValueError("encoder metadata is required")
    _text(encoder.get("id"), "encoder.id")
    _text(encoder.get("revision"), "encoder.revision")
    dimension = _integer(encoder.get("dimension"), "encoder.dimension", 1)

    def item(raw: Any, objective: bool = False) -> dict[str, Any]:
        if not isinstance(raw, dict):
            raise ValueError("objective and cues must be JSON objects")
        result = dict(raw)
        _text(raw.get("id"), "item.id")
        if "encoder" in raw and raw["encoder"] != encoder:
            raise ValueError(f"{raw['id']}: mixed encoder metadata is not allowed")
        if objective:
            _text(raw.get("text"), "objective.text")
        else:
            _text(raw.get("label"), "cue.label")
            _text(raw.get("source"), "cue.source")
            if raw.get("kind") not in ("text", "image"):
                raise ValueError("cue.kind must be text or image")
        try:
            result["embedding"] = normalize_embedding(raw.get("embedding"), dimension)
        except ValueError as exc:
            raise ValueError(f"{raw['id']}: {exc}") from exc
        return result

    objective = item(payload.get("objective"), objective=True)
    raw_cues = payload.get("cues")
    if not isinstance(raw_cues, list):
        raise ValueError("cues must be an array (which may be empty)")
    cues = [item(raw) for raw in raw_cues]
    ids = [objective["id"], *(cue["id"] for cue in cues)]
    if len(ids) != len(set(ids)):
        raise ValueError("objective and cue ids must be unique")
    operators = payload.get("operators")
    if not isinstance(operators, list) or not operators:
        raise ValueError("operators must be a nonempty array")
    for operator in operators:
        _text(operator, "operator")
    if len(set(operators)) != len(operators):
        raise ValueError("operators must be unique")
    return {"encoder": dict(encoder), "objective": objective,
            "cues": cues, "operators": list(operators)}


def validate_weights(weights: Any) -> tuple[float, float, float]:
    if not isinstance(weights, (list, tuple)) or len(weights) != 3:
        raise ValueError("weights must contain near, middle, far values")
    if any(isinstance(x, bool) or not isinstance(x, (int, float)) for x in weights):
        raise ValueError("weights must be positive finite numbers")
    try:
        values = tuple(float(x) for x in weights)
    except OverflowError as exc:
        raise ValueError("weights must be positive finite numbers") from exc
    if any(not math.isfinite(x) or x <= 0 for x in values):
        raise ValueError("weights must be positive finite numbers")
    scale = max(values)
    scaled = tuple(x / scale for x in values)
    if any(x == 0 for x in scaled):
        raise ValueError("relative weights are too small to represent positive sampling probabilities")
    total = math.fsum(scaled)
    return tuple(x / total for x in scaled)


def transition_distribution(
    current_vector: Any,
    cues: list[dict[str, Any]],
    weights: Any = DEFAULT_WEIGHTS,
) -> list[dict[str, Any]]:
    """Return the exact cue distribution, ordered by kind then distance.

    Available kinds receive equal probability, preventing one modality from
    occupying an entire pooled distance band. Within each kind, balanced rank
    terciles receive extra items in near, then middle. Ties are broken by cue id.
    Empty bands receive no mass; other weights are renormalized. Each member of
    a band has equal conditional probability.
    """
    normalized_weights = validate_weights(weights)
    if not cues:
        return []
    rows = []
    kinds = sorted({cue["kind"] for cue in cues})
    for kind in kinds:
        ranked = sorted(
            ((cosine_distance(current_vector, cue["embedding"]), cue["id"])
             for cue in cues if cue["kind"] == kind),
            key=lambda pair: (pair[0], pair[1]),
        )
        size, extra = divmod(len(ranked), 3)
        sizes = [size + (index < extra) for index in range(3)]
        mass = math.fsum(w for w, count in zip(normalized_weights, sizes) if count)
        offset = 0
        for band, count, weight in zip(BANDS, sizes, normalized_weights):
            if not count:
                continue
            band_probability = weight / mass
            for distance, cue_id in ranked[offset:offset + count]:
                rows.append({"cue_id": cue_id, "kind": kind, "band": band,
                             "kind_probability": 1.0 / len(kinds),
                             "distance_to_parent": distance, "band_size": count,
                             "band_probability": band_probability,
                             "probability": band_probability / (count * len(kinds))})
            offset += count
    return rows


def _draw(distribution: list[dict[str, Any]], rng: random.Random) -> dict[str, Any]:
    threshold = rng.random()
    cumulative = 0.0
    for item in distribution:
        cumulative += item["probability"]
        if threshold < cumulative:
            return item
    return distribution[-1]  # Floating-point accumulation may end just below 1.


def run_walks(
    payload: Any, *, seed: int, walks: int = 3, hops: int = 3,
    weights: Any = DEFAULT_WEIGHTS,
) -> dict[str, Any]:
    """Sample cue paths; returned results are deterministic for the same input."""
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise ValueError("seed must be an integer")
    _integer(walks, "walks", 1)
    _integer(hops, "hops", 1)
    data = validate_input(payload)
    normalized_weights = validate_weights(weights)
    try:
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"),
                               ensure_ascii=False, allow_nan=False).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise ValueError("input must contain only finite JSON-serializable values") from exc
    rng = random.Random(seed)
    objective = data["objective"]
    cues = data["cues"]
    by_id = {cue["id"]: cue for cue in cues}
    archive: dict[str, dict[str, Any]] = {}
    paths = []
    for path_index in range(walks):
        current = objective
        visited: set[str] = set()
        steps = []
        for hop_index in range(min(hops, len(cues))):
            available = [cue for cue in cues if cue["id"] not in visited]
            distribution = transition_distribution(current["embedding"], available,
                                                     normalized_weights)
            selected = _draw(distribution, rng)
            cue = by_id[selected["cue_id"]]
            operator = rng.choice(data["operators"])
            novelty = min(
                (cosine_distance(cue["embedding"], earlier["embedding"])
                 for earlier in archive.values()), default=None,
            )
            steps.append({
                "hop": hop_index + 1,
                "previous_id": current["id"], "current_id": cue["id"],
                "selected_kind": selected["kind"],
                "kind_probability": selected["kind_probability"],
                "selected_band": selected["band"],
                "distance_to_parent": selected["distance_to_parent"],
                "distance_to_objective": cosine_distance(cue["embedding"], objective["embedding"]),
                "min_distance_to_earlier_cues": novelty,
                "available_cues": len(available),
                "band_sizes_within_selected_kind": {
                    band: sum(row["band"] == band and row["kind"] == selected["kind"]
                              for row in distribution)
                               for band in BANDS},
                "selected_band_probability": selected["band_probability"],
                "transition_probability": selected["probability"],
                "operator": operator,
                "operator_probability": 1.0 / len(data["operators"]),
                "joint_probability": selected["probability"] / len(data["operators"]),
            })
            visited.add(cue["id"])
            archive[cue["id"]] = cue
            current = cue
        paths.append({"path_id": f"path_{path_index + 1:02d}", "steps": steps,
                      "termination": "pool_exhausted" if len(cues) <= hops else "hop_budget_reached"})
    def metadata(item: dict[str, Any]) -> dict[str, Any]:
        return {key: value for key, value in item.items() if key not in ("embedding", "encoder")}

    return {
        "schema_version": "1.0", "status": "sampled_cues_only",
        "input_sha256": hashlib.sha256(canonical).hexdigest(),
        "hash_format": "canonical JSON; sorted keys, compact separators, UTF-8",
        "encoder": data["encoder"],
        "config": {"seed": seed, "walks": walks, "hops": hops,
                   "band_weights": dict(zip(BANDS, normalized_weights)),
                   "kind_sampling": "uniform over available kinds before distance bands",
                   "rank_bands": "within kind: balanced terciles; extras near then middle; ties by id",
                   "metric": "1 - cosine similarity of normalized supplied vectors",
                   "operator_sampling": "uniform", "operators": data["operators"]},
        "objective": metadata(objective), "cues": [metadata(cue) for cue in cues],
        "paths": paths,
        "observed_hops": sum(len(path["steps"]) for path in paths),
        "utility_assessed": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="JSON containing supplied shared-space embeddings")
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--walks", type=int, default=3)
    parser.add_argument("--hops", type=int, default=3)
    parser.add_argument("--weights", type=float, nargs=3, metavar=("NEAR", "MIDDLE", "FAR"),
                        default=DEFAULT_WEIGHTS)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        result = run_walks(payload, seed=args.seed, walks=args.walks, hops=args.hops,
                           weights=args.weights)
        if args.output.resolve() == args.input.resolve():
            raise ValueError("output must not overwrite input")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
                               encoding="utf-8")
    except (ValueError, OSError) as exc:
        print(f"semantic_walk: {exc}", file=sys.stderr)
        return 2
    print(f"Sampled {result['observed_hops']} cue transitions into {args.output}; utility not assessed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
