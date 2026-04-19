#!/usr/bin/env python3
"""
Typed schema and validation helpers for stochastic perturbation bridge outputs.
"""

from __future__ import annotations

import argparse
import base64
import json
import re
import sys
from dataclasses import asdict
from dataclasses import dataclass
from typing import Literal


BridgeType = Literal[
    "structural_isomorphism",
    "negation_revelation",
    "compositional_insight",
    "none",
]

ALLOWED_BRIDGE_TYPES = {
    "structural_isomorphism",
    "negation_revelation",
    "compositional_insight",
    "none",
}

DEFAULT_RESULT_DELIMITER = "===SEED_RESULT==="


class BridgeSchemaError(ValueError):
    """Raised when a seed-agent result violates the schema."""


@dataclass(frozen=True)
class SeedAgentResult:
    story: str
    story_predicates: list[str]
    bridge_type: BridgeType
    bridge_predicates: list[str]
    counterevidence: str
    reflection: str
    signal: int

    def to_dict(self) -> dict:
        """Return the full normalized result."""
        return asdict(self)

    def to_watcher_record(self) -> dict:
        """Return the subset of fields the watcher is allowed to see."""
        return {
            "bridge_type": self.bridge_type,
            "bridge_predicates": self.bridge_predicates,
            "counterevidence": self.counterevidence,
            "reflection": self.reflection,
            "signal": self.signal,
        }


def strip_json_fences(raw: str) -> str:
    """Strip optional Markdown fences from an LLM JSON response."""
    text = raw.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


def _normalize_predicate_list(value, field_name: str) -> list[str]:
    """Normalize predicate fields into non-empty string lists."""
    if isinstance(value, list):
        items = value
    elif isinstance(value, str):
        items = [item.strip(" -") for item in re.split(r"[\n;]+", value) if item.strip()]
    else:
        raise BridgeSchemaError(f"{field_name} must be a list of strings or a newline-delimited string.")

    normalized = []
    for item in items:
        if not isinstance(item, str):
            raise BridgeSchemaError(f"{field_name} entries must be strings.")
        cleaned = item.strip()
        if cleaned:
            normalized.append(cleaned)
    return normalized


def _require_string(payload: dict, field_name: str, minimum_length: int) -> str:
    value = payload.get(field_name)
    if not isinstance(value, str):
        raise BridgeSchemaError(f"{field_name} must be a string.")
    value = value.strip()
    if len(value) < minimum_length:
        raise BridgeSchemaError(f"{field_name} must be at least {minimum_length} characters.")
    return value


def validate_seed_agent_payload(payload: dict) -> SeedAgentResult:
    """Validate and normalize a raw JSON payload."""
    if not isinstance(payload, dict):
        raise BridgeSchemaError("Seed-agent result must be a JSON object.")

    required_fields = {
        "story",
        "story_predicates",
        "bridge_type",
        "bridge_predicates",
        "counterevidence",
        "reflection",
        "signal",
    }
    missing = required_fields - payload.keys()
    if missing:
        missing_fields = ", ".join(sorted(missing))
        raise BridgeSchemaError(f"Missing required fields: {missing_fields}")

    story = _require_string(payload, "story", minimum_length=20)
    story_predicates = _normalize_predicate_list(payload["story_predicates"], "story_predicates")
    if not story_predicates:
        raise BridgeSchemaError("story_predicates must not be empty.")

    bridge_type = payload["bridge_type"]
    if bridge_type not in ALLOWED_BRIDGE_TYPES:
        allowed = ", ".join(sorted(ALLOWED_BRIDGE_TYPES))
        raise BridgeSchemaError(f"bridge_type must be one of: {allowed}")

    bridge_predicates = _normalize_predicate_list(payload["bridge_predicates"], "bridge_predicates")
    counterevidence = _require_string(payload, "counterevidence", minimum_length=20)
    reflection = _require_string(payload, "reflection", minimum_length=40)

    signal = payload["signal"]
    if not isinstance(signal, int):
        raise BridgeSchemaError("signal must be an integer.")
    if signal < 0 or signal > 5:
        raise BridgeSchemaError("signal must be between 0 and 5.")

    if bridge_type == "none":
        if bridge_predicates:
            raise BridgeSchemaError("bridge_predicates must be empty when bridge_type is 'none'.")
        if signal > 1:
            raise BridgeSchemaError("signal must be 0 or 1 when bridge_type is 'none'.")
    else:
        if not bridge_predicates:
            raise BridgeSchemaError("bridge_predicates must not be empty when bridge_type is not 'none'.")
        if signal == 0:
            raise BridgeSchemaError("signal must be at least 1 when a bridge is present.")

    return SeedAgentResult(
        story=story,
        story_predicates=story_predicates,
        bridge_type=bridge_type,
        bridge_predicates=bridge_predicates,
        counterevidence=counterevidence,
        reflection=reflection,
        signal=signal,
    )


def parse_seed_agent_result(raw: str) -> SeedAgentResult:
    """Parse a seed-agent response into a validated typed result."""
    try:
        payload = json.loads(strip_json_fences(raw))
    except json.JSONDecodeError as exc:
        raise BridgeSchemaError(f"Seed-agent result is not valid JSON: {exc}") from exc
    return validate_seed_agent_payload(payload)


def normalize_seed_agent_result(entry) -> SeedAgentResult:
    """Normalize either a raw string or a decoded JSON object."""
    if isinstance(entry, str):
        return parse_seed_agent_result(entry)
    if isinstance(entry, dict):
        return validate_seed_agent_payload(entry)
    raise BridgeSchemaError("Seed-agent result must be a raw JSON string or decoded JSON object.")


def parse_seed_result_batch(raw: str, delimiter: str = DEFAULT_RESULT_DELIMITER) -> list:
    """Parse stdin into a batch of raw seed results."""
    text = raw.strip()
    if not text:
        return []

    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        blocks = [block.strip() for block in text.split(delimiter) if block.strip()]
        if not blocks:
            raise BridgeSchemaError("No seed-agent results found in stdin.")
        return blocks

    if isinstance(payload, list):
        return payload

    raise BridgeSchemaError("Batch input must be either a JSON array or delimiter-separated raw results.")


def render_watcher_payload(results: list[SeedAgentResult]) -> str:
    """Render validated seed-agent outputs into the watcher's JSON payload."""
    return json.dumps(
        [result.to_watcher_record() for result in results],
        ensure_ascii=False,
        indent=2,
    )


def build_completed_watcher_prompt(prompt_template: str, payload: str) -> str:
    """Replace the watcher payload placeholder with validated seed output."""
    placeholder = "{{SEED_AGENT_RESULTS}}"
    if placeholder not in prompt_template:
        raise BridgeSchemaError("Watcher prompt template does not contain the required payload placeholder.")
    return prompt_template.replace(placeholder, payload)


def compile_watcher_payload(
    entries: list,
    *,
    strict: bool = False,
) -> tuple[str, list[str], list[SeedAgentResult]]:
    """Validate a batch of seed-agent entries and build watcher payload JSON."""
    valid_results: list[SeedAgentResult] = []
    errors: list[str] = []

    for index, entry in enumerate(entries, start=1):
        try:
            valid_results.append(normalize_seed_agent_result(entry))
        except BridgeSchemaError as exc:
            error = f"seed {index}: {exc}"
            errors.append(error)
            if strict:
                raise BridgeSchemaError(error) from exc

    if not valid_results:
        raise BridgeSchemaError("No valid seed-agent results were available for watcher payload generation.")

    return render_watcher_payload(valid_results), errors, valid_results


def _read_stdin_or_file(input_file: str | None) -> str:
    """Read command input from a file or stdin."""
    if input_file:
        return open(input_file, "r", encoding="utf-8").read()
    return sys.stdin.read()


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate seed-agent results and build watcher payloads.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate one seed-agent result and print normalized JSON.",
    )
    validate_parser.add_argument(
        "--input-file",
        type=str,
        help="Optional path to a file containing one raw seed-agent result.",
    )

    watcher_parser = subparsers.add_parser(
        "watcher-payload",
        help="Validate seed-agent results and emit the watcher-safe JSON array.",
    )
    watcher_parser.add_argument(
        "--input-file",
        type=str,
        help="Optional path to a file containing either a JSON array or delimiter-separated raw results.",
    )
    watcher_parser.add_argument(
        "--delimiter",
        type=str,
        default=DEFAULT_RESULT_DELIMITER,
        help="Delimiter used when stdin is not JSON. Default: %(default)s",
    )
    watcher_parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail if any seed-agent result is invalid instead of dropping invalid entries.",
    )

    watcher_prompt_parser = subparsers.add_parser(
        "watcher-prompt",
        help="Validate seed-agent results and emit the completed watcher prompt.",
    )
    watcher_prompt_parser.add_argument(
        "--input-file",
        type=str,
        help="Optional path to a file containing either a JSON array or delimiter-separated raw results.",
    )
    watcher_prompt_parser.add_argument(
        "--prompt-b64",
        type=str,
        required=True,
        help="Base64-encoded watcher prompt template containing {{SEED_AGENT_RESULTS}}.",
    )
    watcher_prompt_parser.add_argument(
        "--delimiter",
        type=str,
        default=DEFAULT_RESULT_DELIMITER,
        help="Delimiter used when stdin is not JSON. Default: %(default)s",
    )
    watcher_prompt_parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail if any seed-agent result is invalid instead of dropping invalid entries.",
    )
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    try:
        raw_input = _read_stdin_or_file(getattr(args, "input_file", None))

        if args.command == "validate":
            result = parse_seed_agent_result(raw_input)
            print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
            return 0

        if args.command == "watcher-payload":
            entries = parse_seed_result_batch(raw_input, delimiter=args.delimiter)
            payload, errors, valid_results = compile_watcher_payload(entries, strict=args.strict)
            for error in errors:
                print(f"WARNING: {error}", file=sys.stderr)
            print(
                f"Accepted {len(valid_results)} of {len(entries)} seed-agent results.",
                file=sys.stderr,
            )
            print(payload)
            return 0

        if args.command == "watcher-prompt":
            entries = parse_seed_result_batch(raw_input, delimiter=args.delimiter)
            payload, errors, valid_results = compile_watcher_payload(entries, strict=args.strict)
            prompt_template = base64.b64decode(args.prompt_b64).decode("utf-8")
            completed_prompt = build_completed_watcher_prompt(prompt_template, payload)
            for error in errors:
                print(f"WARNING: {error}", file=sys.stderr)
            print(
                f"Accepted {len(valid_results)} of {len(entries)} seed-agent results.",
                file=sys.stderr,
            )
            print(completed_prompt)
            return 0

        parser.error(f"Unsupported command: {args.command}")
    except BridgeSchemaError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
