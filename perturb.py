#!/usr/bin/env python3
"""
Stochastic Perturbation — Seed Generator (Stage C, Phase 1)

Computational seed generation for the via-negativa stochastic perturbation
protocol. Handles ONLY the math: entropy extraction, SHA-256 hashing, and
NLLB-200 multilingual token sampling. No API key required.

Agent spawning (Phase 2) is handled by the skill's imperative instructions
within the Claude conversation — not by this script.

Usage:
  python perturb.py --seeds-only --artifact "text..."
  python perturb.py --seeds-only --artifact-file path/to/artifact.txt
  python perturb.py --seeds-only --artifact "text..." --rounds 2 --seeds 4 --tokens 7
  python perturb.py --seeds-only --artifact "text..." --round 2  # specific round number

Requires:
  pip install sentencepiece transformers
"""

import argparse
import hashlib
import json
import random
import re
import sys
from pathlib import Path


def extract_entropy(text: str) -> list[str]:
    """Extract numerical features from artifact text for seeding RNG."""
    lower = text.lower()
    return [
        str(sum(1 for c in lower if c in "aeiou")),
        str(sum(1 for c in lower if c.isalpha() and c not in "aeiou")),
        str(len(text)),
        str(text.count(".")),
        str(text.count(" ")),
        str(len(text.split("."))),
    ]


def generate_seeds(features: list[str], n: int, round_num: int = 0) -> list[int]:
    """Hash features into N deterministic seeds. round_num shifts the hash."""
    payload = "|".join(features)
    if round_num > 0:
        payload = payload[::-1] + f"|round={round_num}"
    digest = hashlib.sha256(payload.encode()).hexdigest()
    return [int(digest[i : i + 16], 16) for i in range(0, n * 16, 16)]


def load_tokenizer():
    """Load NLLB-200 tokenizer and filter to pure word tokens (~213K tokens, 15+ scripts)."""
    try:
        from transformers import AutoTokenizer
    except ImportError:
        print("ERROR: pip install sentencepiece transformers", file=sys.stderr)
        sys.exit(1)

    print("Loading NLLB-200 tokenizer...", file=sys.stderr)
    tok = AutoTokenizer.from_pretrained("facebook/nllb-200-distilled-600M")
    vocab = tok.get_vocab()

    pure_word = re.compile(
        r"^[\u0041-\u005A\u0061-\u007A\u00C0-\u024F"
        r"\u0400-\u04FF\u0600-\u06FF\u0900-\u097F"
        r"\u0980-\u09FF\u0A00-\u0A7F\u0B00-\u0B7F"
        r"\u0C00-\u0C7F\u0D00-\u0D7F\u0E00-\u0E7F"
        r"\u1000-\u109F\u3040-\u30FF\u3400-\u9FFF"
        r"\uAC00-\uD7AF\u4E00-\u9FFF\u0530-\u058F"
        r"\u10A0-\u10FF]+$"
    )

    word_tokens = [
        (tid, s.replace("\u2581", ""))
        for s, tid in vocab.items()
        if pure_word.match(s.replace("\u2581", "")) and len(s.replace("\u2581", "")) >= 2
    ]
    print(f"Filtered vocab: {len(word_tokens)} word tokens", file=sys.stderr)
    return word_tokens


def sample_tokens(word_tokens: list, seeds: list[int], k: int) -> dict[str, list[str]]:
    """Sample K random tokens per seed from multilingual vocabulary."""
    result = {}
    for i, seed in enumerate(seeds):
        rng = random.Random(seed)
        selected = rng.sample(word_tokens, k)
        result[f"seed_{i + 1}"] = [t[1] for t in selected]
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Stochastic Perturbation — Seed Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--artifact", type=str, help="Thinker's artifact text")
    parser.add_argument("--artifact-file", type=str, help="Path to artifact text file")
    parser.add_argument("--rounds", type=int, default=1, help="Number of rounds to generate (default: 1)")
    parser.add_argument("--round", type=int, default=None, help="Specific round number (for iteration)")
    parser.add_argument("--seeds", type=int, default=3, help="Seeds per round (default: 3)")
    parser.add_argument("--tokens", type=int, default=6, help="Tokens per seed (default: 6)")
    parser.add_argument("--seeds-only", action="store_true", default=True, help="(default, kept for compatibility)")

    args = parser.parse_args()

    # Load artifact
    artifact = args.artifact
    if args.artifact_file:
        artifact = Path(args.artifact_file).read_text()
    if not artifact:
        parser.error("Provide --artifact or --artifact-file")

    word_tokens = load_tokenizer()
    features = extract_entropy(artifact)

    if args.round is not None:
        # Single specific round
        seeds = generate_seeds(features, args.seeds, args.round)
        seed_tokens = sample_tokens(word_tokens, seeds, args.tokens)
        print(json.dumps({"round": args.round, "seeds": seed_tokens}, ensure_ascii=False, indent=2))
    else:
        # Multiple rounds
        for round_num in range(args.rounds):
            seeds = generate_seeds(features, args.seeds, round_num)
            seed_tokens = sample_tokens(word_tokens, seeds, args.tokens)
            print(json.dumps({"round": round_num + 1, "seeds": seed_tokens}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
