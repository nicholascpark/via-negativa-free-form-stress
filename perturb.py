#!/usr/bin/env python3
"""
Stochastic Perturbation — Seed Generator & Orchestrator (Stage C)

Computational seed generation and execution manifest builder for the
via-negativa stochastic perturbation protocol. Handles the math
(artifact fingerprinting, deterministic seed expansion, stratified
multilingual token sampling) and the orchestration (complete agent
prompts, scoring formulas, iteration). No API key required.

Usage:
  # Seed generation only (original mode)
  python perturb.py --artifact "text..."
  python perturb.py --artifact-file path/to/artifact.txt

  # Full orchestrator manifest
  python perturb.py --orchestrate \\
    --artifact "text..." \\
    --concern-summary "thinker's concern" \\
    --predicates "Plans(thinker, X)" \\
    --stage-b-synthesis "pattern in negative space"

  # Iteration (uses persisted /tmp files from first call)
  python perturb.py --orchestrate --artifact-file /tmp/vn-artifact.txt \\
    --predicates-file /tmp/vn-predicates.txt \\
    --concern-file /tmp/vn-concern.txt \\
    --stage-b-file /tmp/vn-stageb.txt --round 2

Requires:
  pip install sentencepiece transformers
"""

import argparse
import base64
import hashlib
import json
import os
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

# Portable import: ensure prompt_templates.py is found regardless of cwd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from prompt_templates import render_seed_agent_prompt, render_watcher_prompt


DEFAULT_EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

STOPWORDS = {
    "about", "after", "again", "against", "because", "before", "being",
    "between", "could", "every", "first", "from", "have", "into",
    "just", "might", "only", "other", "over", "same", "should",
    "some", "than", "that", "their", "there", "these", "they",
    "this", "those", "through", "under", "until", "very", "what",
    "when", "where", "which", "while", "with", "would", "your",
    "ours", "ourselves", "itself", "herself", "himself", "themselves",
    "also", "them", "were", "been", "will", "shall", "must",
    "need", "want", "like", "into", "onto", "than", "then",
    "plan", "plans", "idea", "ideas", "thinking", "thinker",
}


def _dot(left: list[float], right: list[float]) -> float:
    """Compute a dot product for normalized embedding vectors."""
    return sum(a * b for a, b in zip(left, right))


def normalize_artifact(text: str) -> str:
    """Normalize artifact text before hashing."""
    return re.sub(r"\s+", " ", text.strip().lower())


def tokenize_words(text: str) -> list[str]:
    """Extract unicode words while dropping digits and underscores."""
    return re.findall(r"[^\W\d_]+", text.lower(), flags=re.UNICODE)


def split_sentences(text: str) -> list[str]:
    """Approximate sentence boundaries for round diversification."""
    return [chunk.strip() for chunk in re.split(r"[.!?]+", text) if chunk.strip()]


def extract_content_words(text: str) -> list[str]:
    """Return content-leaning words for anchor extraction."""
    return [
        word for word in tokenize_words(text)
        if len(word) >= 4 and word not in STOPWORDS
    ]


def extract_anchor_terms(text: str, limit: int = 6) -> list[str]:
    """Extract stable lexical anchors from the artifact."""
    content_words = extract_content_words(text)
    counts = Counter(content_words)
    if not counts:
        counts = Counter(word for word in tokenize_words(text) if len(word) >= 3)
    return [word for word, _ in counts.most_common(limit)]


def extract_character_trigrams(text: str, limit: int = 8) -> list[str]:
    """Extract common character trigrams to diversify later rounds."""
    normalized = normalize_artifact(text).replace(" ", "_")
    if len(normalized) < 3:
        return [normalized] if normalized else []

    trigrams = Counter(
        normalized[idx: idx + 3]
        for idx in range(len(normalized) - 2)
        if normalized[idx: idx + 3].strip("_")
    )
    return [trigram for trigram, _ in trigrams.most_common(limit)]


def classify_char_script(char: str) -> str:
    """Classify a single unicode character into a coarse script family."""
    codepoint = ord(char)
    if 0x0041 <= codepoint <= 0x005A or 0x0061 <= codepoint <= 0x007A or 0x00C0 <= codepoint <= 0x024F:
        return "latin"
    if 0x0400 <= codepoint <= 0x04FF:
        return "cyrillic"
    if 0x0600 <= codepoint <= 0x06FF:
        return "arabic"
    if 0x0900 <= codepoint <= 0x097F:
        return "devanagari"
    if 0x0980 <= codepoint <= 0x09FF:
        return "bengali"
    if 0x0A00 <= codepoint <= 0x0A7F:
        return "gurmukhi"
    if 0x0B00 <= codepoint <= 0x0B7F:
        return "oriya"
    if 0x0C00 <= codepoint <= 0x0C7F:
        return "telugu"
    if 0x0D00 <= codepoint <= 0x0D7F:
        return "malayalam"
    if 0x0E00 <= codepoint <= 0x0E7F:
        return "thai"
    if 0x1000 <= codepoint <= 0x109F:
        return "myanmar"
    if 0x3040 <= codepoint <= 0x309F or 0x30A0 <= codepoint <= 0x30FF:
        return "kana"
    if 0x3400 <= codepoint <= 0x9FFF or 0x4E00 <= codepoint <= 0x9FFF:
        return "cjk"
    if 0xAC00 <= codepoint <= 0xD7AF:
        return "hangul"
    if 0x0530 <= codepoint <= 0x058F:
        return "armenian"
    if 0x10A0 <= codepoint <= 0x10FF:
        return "georgian"
    return "other"


def classify_token_script(token: str) -> str:
    """Infer the dominant script for a token."""
    counts = Counter(
        classify_char_script(char)
        for char in token
        if char.isalpha()
    )
    counts.pop("other", None)
    if not counts:
        return "other"
    return counts.most_common(1)[0][0]


def extract_dominant_scripts(text: str, limit: int = 3) -> list[str]:
    """Return the dominant scripts in the artifact."""
    counts = Counter(
        classify_char_script(char)
        for char in text
        if char.isalpha()
    )
    counts.pop("other", None)
    if not counts:
        return ["latin"]
    return [script for script, _ in counts.most_common(limit)]


def extract_artifact_fingerprint(text: str) -> dict:
    """Build a richer artifact fingerprint than surface counts alone."""
    normalized = normalize_artifact(text)
    words = tokenize_words(normalized)
    sentences = split_sentences(text)
    punctuation_counts = {
        symbol: text.count(symbol)
        for symbol in [".", ",", ";", ":", "?", "!"]
    }

    unique_ratio = len(set(words)) / max(len(words), 1)
    return {
        "normalized_sha256": hashlib.sha256(normalized.encode("utf-8")).hexdigest(),
        "char_count": len(text),
        "word_count": len(words),
        "sentence_count": max(len(sentences), 1),
        "unique_word_ratio": round(unique_ratio, 4),
        "anchor_terms": extract_anchor_terms(text),
        "character_trigrams": extract_character_trigrams(text),
        "dominant_scripts": extract_dominant_scripts(text),
        "punctuation_vector": punctuation_counts,
    }


class EmbeddingScorer:
    """Lazy multilingual embedding scorer for semantic displacement."""

    def __init__(self, model_name: str = DEFAULT_EMBEDDING_MODEL):
        self.model_name = model_name
        self._model = None
        self._tokenizer = None
        self._torch = None
        self._cache: dict[str, list[float]] = {}

    @staticmethod
    def dependencies_available() -> bool:
        """Return whether the embedding stack is importable."""
        try:
            import torch  # noqa: F401
            from transformers import AutoModel, AutoTokenizer  # noqa: F401
            return True
        except Exception:
            return False

    def ensure_loaded(self):
        """Load tokenizer and encoder lazily."""
        if self._model is not None and self._tokenizer is not None:
            return

        import torch
        from transformers import AutoModel, AutoTokenizer

        self._torch = torch
        self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self._model = AutoModel.from_pretrained(self.model_name)
        self._model.eval()

    def encode(self, texts: list[str]):
        """Embed texts and cache normalized vectors."""
        missing = [text for text in dict.fromkeys(texts) if text not in self._cache]
        if not missing:
            return

        self.ensure_loaded()
        encoded = self._tokenizer(
            missing,
            padding=True,
            truncation=True,
            max_length=64,
            return_tensors="pt",
        )

        with self._torch.no_grad():
            model_output = self._model(**encoded)

        attention_mask = encoded["attention_mask"].unsqueeze(-1)
        masked = model_output.last_hidden_state * attention_mask
        summed = masked.sum(dim=1)
        counts = attention_mask.sum(dim=1).clamp(min=1)
        embeddings = summed / counts
        embeddings = self._torch.nn.functional.normalize(embeddings, p=2, dim=1)

        for text, vector in zip(missing, embeddings.tolist()):
            self._cache[text] = vector

    def similarity_to_anchors(self, candidates: list[str], anchors: list[str]) -> dict[str, float]:
        """Return max cosine similarity between each candidate and the anchor set."""
        if not anchors:
            return {candidate: 0.0 for candidate in candidates}

        texts = list(dict.fromkeys(candidates + anchors))
        self.encode(texts)
        anchor_vectors = [self._cache[anchor] for anchor in anchors]

        return {
            candidate: max(_dot(self._cache[candidate], anchor_vector) for anchor_vector in anchor_vectors)
            for candidate in candidates
        }


def resolve_displacement_mode(displacement_mode: str, embedding_model: str) -> tuple[str, EmbeddingScorer | None, str]:
    """Resolve lexical vs embedding displacement and load dependencies if needed."""
    if displacement_mode == "lexical":
        return "lexical", None, "lexical displacement only"

    if not EmbeddingScorer.dependencies_available():
        if displacement_mode == "auto":
            return "lexical", None, "embedding dependencies unavailable; falling back to lexical displacement"
        raise RuntimeError(
            "Embedding displacement requires torch and transformers with model loading support."
        )

    scorer = EmbeddingScorer(embedding_model)
    try:
        scorer.ensure_loaded()
    except Exception as exc:
        if displacement_mode == "auto":
            return "lexical", None, f"embedding model load failed ({exc}); falling back to lexical displacement"
        raise RuntimeError(
            f"Failed to load embedding model '{embedding_model}': {exc}"
        ) from exc

    if displacement_mode == "auto":
        return "hybrid", scorer, f"hybrid displacement using {embedding_model}"
    return displacement_mode, scorer, f"{displacement_mode} displacement using {embedding_model}"


def build_round_profile(text: str, round_num: int, fingerprint: dict | None = None) -> dict:
    """Construct the round-specific perturbation strategy."""
    fingerprint = fingerprint or extract_artifact_fingerprint(text)
    normalized = normalize_artifact(text)
    sentences = split_sentences(text)
    content_counts = Counter(extract_content_words(text))
    rare_words = [
        word for word, _ in sorted(content_counts.items(), key=lambda item: (item[1], item[0]))[:8]
    ]

    strategies = [
        {
            "name": "surface_fingerprint",
            "description": "Hash the normalized artifact text to keep the first pass close to the original surface.",
            "payload": normalized,
        },
        {
            "name": "sentence_mirror",
            "description": "Reverse sentence order and foreground boundaries to perturb temporal and rhetorical flow.",
            "payload": " || ".join(reversed(sentences)) if sentences else normalized[::-1],
        },
        {
            "name": "negative_lexicon",
            "description": "Hash anchor terms, rare words, and character trigrams to push later rounds away from the artifact's default phrasing.",
            "payload": " | ".join(
                fingerprint["anchor_terms"][::-1] + rare_words + fingerprint["character_trigrams"]
            ) or normalized,
        },
    ]

    index = (round_num - 1) % len(strategies)
    cycle = (round_num - 1) // len(strategies)
    strategy = dict(strategies[index])
    strategy["cycle"] = cycle
    strategy["round"] = round_num
    return strategy


def build_seed_material(text: str, round_num: int, fingerprint: dict | None = None, round_profile: dict | None = None) -> str:
    """Serialize seed material for deterministic hash expansion."""
    fingerprint = fingerprint or extract_artifact_fingerprint(text)
    round_profile = round_profile or build_round_profile(text, round_num, fingerprint)
    payload = {
        "artifact_hash": fingerprint["normalized_sha256"],
        "round_strategy": round_profile["name"],
        "round_cycle": round_profile["cycle"],
        "round_payload": round_profile["payload"],
        "anchor_terms": fingerprint["anchor_terms"],
        "dominant_scripts": fingerprint["dominant_scripts"],
        "punctuation_vector": fingerprint["punctuation_vector"],
    }
    return json.dumps(payload, sort_keys=True, ensure_ascii=False)


def generate_seeds(
    text: str,
    n: int,
    round_num: int = 1,
    fingerprint: dict | None = None,
    round_profile: dict | None = None,
) -> list[int]:
    """Expand deterministic seed material into an arbitrary number of seeds."""
    seed_material = build_seed_material(text, round_num, fingerprint, round_profile)
    seeds = []
    counter = 0
    while len(seeds) < n:
        digest = hashlib.blake2b(
            f"{seed_material}|seed={counter}".encode("utf-8"),
            digest_size=16,
        ).digest()
        seeds.append(int.from_bytes(digest, "big"))
        counter += 1
    return seeds


def token_anchor_overlap(token: str, anchor_terms: list[str]) -> float:
    """Measure token overlap against artifact anchors using char bigrams."""
    if not anchor_terms:
        return 0.0

    def bigrams(text: str) -> set[str]:
        if len(text) < 2:
            return {text}
        return {text[idx: idx + 2] for idx in range(len(text) - 1)}

    token_bigrams = bigrams(token.lower())
    best_overlap = 0.0
    for anchor in anchor_terms:
        anchor_bigrams = bigrams(anchor.lower())
        union = token_bigrams | anchor_bigrams
        if not union:
            continue
        overlap = len(token_bigrams & anchor_bigrams) / len(union)
        best_overlap = max(best_overlap, overlap)
    return best_overlap


def load_tokenizer() -> list[dict]:
    """Load NLLB-200 tokenizer and annotate filtered word tokens."""
    try:
        from transformers import AutoTokenizer
    except ImportError:
        print("ERROR: pip install sentencepiece transformers", file=sys.stderr)
        sys.exit(1)

    print("Loading NLLB-200 tokenizer...", file=sys.stderr)
    tokenizer = AutoTokenizer.from_pretrained("facebook/nllb-200-distilled-600M")
    vocab = tokenizer.get_vocab()

    pure_word = re.compile(
        r"^[\u0041-\u005A\u0061-\u007A\u00C0-\u024F"
        r"\u0400-\u04FF\u0600-\u06FF\u0900-\u097F"
        r"\u0980-\u09FF\u0A00-\u0A7F\u0B00-\u0B7F"
        r"\u0C00-\u0C7F\u0D00-\u0D7F\u0E00-\u0E7F"
        r"\u1000-\u109F\u3040-\u30FF\u3400-\u9FFF"
        r"\uAC00-\uD7AF\u4E00-\u9FFF\u0530-\u058F"
        r"\u10A0-\u10FF]+$"
    )

    token_catalog = []
    for serialized, token_id in vocab.items():
        token = serialized.replace("\u2581", "")
        if not pure_word.match(token) or len(token) < 2:
            continue
        token_catalog.append({
            "id": token_id,
            "text": token,
            "script": classify_token_script(token),
            "length": len(token),
        })

    print(f"Filtered vocab: {len(token_catalog)} word tokens", file=sys.stderr)
    return token_catalog


def select_candidate(
    pool: list[dict],
    rng: random.Random,
    used_ids: set[int],
    anchor_terms: list[str],
    dominant_scripts: list[str],
    script_counts: Counter,
    displacement_mode: str,
    embedding_scorer: EmbeddingScorer | None = None,
) -> dict | None:
    """Pick a token that is lexically distant from artifact anchors."""
    available = [entry for entry in pool if entry["id"] not in used_ids]
    if not available:
        return None

    candidates = rng.sample(available, min(len(available), 96))
    semantic_scores = {}
    if embedding_scorer and displacement_mode in {"embedding", "hybrid"}:
        semantic_scores = embedding_scorer.similarity_to_anchors(
            [entry["text"] for entry in candidates],
            anchor_terms,
        )

    return min(
        candidates,
        key=lambda entry: (
            semantic_scores.get(entry["text"], 0.0) if displacement_mode in {"embedding", "hybrid"} else 0.0,
            token_anchor_overlap(entry["text"], anchor_terms) if displacement_mode in {"lexical", "hybrid"} else 0.0,
            + (0.15 if entry["script"] in dominant_scripts else 0.0)
            + 0.05 * script_counts[entry["script"]],
            abs(entry["length"] - 5),
            entry["text"],
        ),
    )


def sample_tokens(
    token_catalog: list[dict],
    seeds: list[int],
    k: int,
    anchor_terms: list[str],
    dominant_scripts: list[str],
    displacement_mode: str = "lexical",
    embedding_scorer: EmbeddingScorer | None = None,
) -> dict[str, dict]:
    """Sample K tokens per seed with script diversity and lexical displacement."""
    script_buckets: dict[str, list[dict]] = defaultdict(list)
    for entry in token_catalog:
        script_buckets[entry["script"]].append(entry)

    scripts = list(script_buckets)
    result = {}
    for index, seed in enumerate(seeds):
        rng = random.Random(seed)
        preferred_scripts = [script for script in scripts if script not in dominant_scripts]
        fallback_scripts = [script for script in scripts if script in dominant_scripts]
        rng.shuffle(preferred_scripts)
        rng.shuffle(fallback_scripts)
        script_order = preferred_scripts + fallback_scripts

        selected = []
        selected_scripts = []
        used_ids: set[int] = set()
        script_counts: Counter = Counter()

        for script in script_order[:min(k, len(script_order))]:
            candidate = select_candidate(
                script_buckets[script],
                rng,
                used_ids,
                anchor_terms,
                dominant_scripts,
                script_counts,
                displacement_mode,
                embedding_scorer,
            )
            if not candidate:
                continue
            selected.append(candidate)
            selected_scripts.append(candidate["script"])
            used_ids.add(candidate["id"])
            script_counts[candidate["script"]] += 1

        while len(selected) < k:
            candidate = select_candidate(
                token_catalog,
                rng,
                used_ids,
                anchor_terms,
                dominant_scripts,
                script_counts,
                displacement_mode,
                embedding_scorer,
            )
            if not candidate:
                break
            selected.append(candidate)
            selected_scripts.append(candidate["script"])
            used_ids.add(candidate["id"])
            script_counts[candidate["script"]] += 1

        result[f"seed_{index + 1}"] = {
            "tokens": [entry["text"] for entry in selected],
            "scripts": selected_scripts,
        }

    return result


def persist_inputs(artifact: str, concern: str, predicates: str, stage_b: str):
    """Write inputs to /tmp for iteration round reuse. Restrict permissions to owner-only."""
    for path, content in [
        ("/tmp/vn-artifact.txt", artifact),
        ("/tmp/vn-concern.txt", concern),
        ("/tmp/vn-predicates.txt", predicates),
    ]:
        Path(path).write_text(content)
        os.chmod(path, 0o600)
    if stage_b:
        Path("/tmp/vn-stageb.txt").write_text(stage_b)
        os.chmod("/tmp/vn-stageb.txt", 0o600)


def build_manifest(
    seed_packets: dict[str, dict],
    concern: str,
    predicates: str,
    stage_b: str,
    round_num: int,
    script_path: str,
    sampler_context: dict,
) -> dict:
    """Build the complete execution manifest with agent prompts."""
    agents = []
    for seed_id, packet in seed_packets.items():
        perturbation_profile = {
            "round_strategy": sampler_context["round_strategy"],
            "round_description": sampler_context["round_description"],
            "artifact_dominant_scripts": sampler_context["artifact_dominant_scripts"],
            "artifact_anchor_terms": sampler_context["artifact_anchor_terms"],
            "sampled_scripts": packet["scripts"],
            "selection_strategy": sampler_context["selection_strategy"],
            "displacement_mode": sampler_context["displacement_mode"],
            "displacement_note": sampler_context["displacement_note"],
        }
        agents.append({
            "id": seed_id,
            "tokens": packet["tokens"],
            "sampled_scripts": packet["scripts"],
            "prompt": render_seed_agent_prompt(
                packet["tokens"],
                concern,
                predicates,
                artifact_anchors=sampler_context["artifact_anchor_terms"],
                perturbation_profile=perturbation_profile,
            ),
        })

    next_round = round_num + 1
    watcher_prompt = render_watcher_prompt(stage_b)
    watcher_prompt_b64 = base64.b64encode(watcher_prompt.encode("utf-8")).decode("ascii")
    manifest = {
        "protocol": "via-negativa-stochastic-perturbation",
        "version": 3,
        "round": round_num,
        "schema": {
            "seed_agent_result_format": "json",
            "seed_agent_result_version": 1,
            "watcher_payload_format": "json-array",
            "watcher_payload_builder_command": (
                "python3 ${CLAUDE_SKILL_DIR}/bridge_schema.py watcher-payload"
            ),
            "watcher_prompt_builder_command": (
                "python3 ${CLAUDE_SKILL_DIR}/bridge_schema.py watcher-prompt"
                f" --prompt-b64 {watcher_prompt_b64}"
            ),
            "seed_result_delimiter": "===SEED_RESULT===",
        },
        "sampler": sampler_context,
        "steps": [
            {
                "step": "seed_agents",
                "dispatch": "parallel",
                "agents": agents,
            },
            {
                "step": "watcher",
                "dispatch": "after_seed_agents",
                "input_from": "seed_agents",
                "input_fields": [
                    "bridge_type",
                    "bridge_predicates",
                    "counterevidence",
                    "reflection",
                    "signal",
                ],
                "stage_b_synthesis": stage_b,
                "prompt": watcher_prompt,
            },
        ],
        "iteration": {
            "signal_threshold": 0.5,
            "max_rounds": 3,
            "next_round_command": (
                f"python3 {script_path} --orchestrate"
                f" --artifact-file /tmp/vn-artifact.txt"
                f" --predicates-file /tmp/vn-predicates.txt"
                f" --concern-file /tmp/vn-concern.txt"
                f" --stage-b-file /tmp/vn-stageb.txt"
                f" --displacement-mode {sampler_context['displacement_mode']}"
                f" --embedding-model {json.dumps(sampler_context['embedding_model'])}"
                f" --round {next_round}"
            ),
        },
    }
    return manifest


def build_sampler_context(
    text: str,
    round_num: int,
    fingerprint: dict,
    round_profile: dict,
    displacement_mode: str,
    embedding_model: str,
    displacement_note: str,
) -> dict:
    """Summarize the sampling logic for inspectability and prompts."""
    return {
        "round_strategy": round_profile["name"],
        "round_description": round_profile["description"],
        "artifact_anchor_terms": fingerprint["anchor_terms"],
        "artifact_dominant_scripts": fingerprint["dominant_scripts"],
        "artifact_fingerprint": {
            "normalized_sha256": fingerprint["normalized_sha256"][:16],
            "char_count": fingerprint["char_count"],
            "word_count": fingerprint["word_count"],
            "sentence_count": fingerprint["sentence_count"],
            "unique_word_ratio": fingerprint["unique_word_ratio"],
        },
        "selection_strategy": (
            "deterministic hash expansion with cross-script selection"
            if displacement_mode == "embedding"
            else "deterministic hash expansion with cross-script, low-overlap token selection"
            if displacement_mode == "lexical"
            else "deterministic hash expansion with cross-script, low-overlap, semantically distant token selection"
        ),
        "displacement_mode": displacement_mode,
        "embedding_model": embedding_model,
        "displacement_note": displacement_note,
        "round": round_num,
    }


def generate_seed_packets(
    text: str,
    token_catalog: list[dict],
    round_num: int,
    seeds_per_round: int,
    tokens_per_seed: int,
    displacement_mode: str = "lexical",
    embedding_model: str = DEFAULT_EMBEDDING_MODEL,
) -> tuple[dict[str, dict], dict]:
    """Generate seed packets and sampler metadata for one round."""
    fingerprint = extract_artifact_fingerprint(text)
    round_profile = build_round_profile(text, round_num, fingerprint)
    seeds = generate_seeds(text, seeds_per_round, round_num, fingerprint, round_profile)
    actual_mode, embedding_scorer, displacement_note = resolve_displacement_mode(
        displacement_mode,
        embedding_model,
    )
    seed_packets = sample_tokens(
        token_catalog,
        seeds,
        tokens_per_seed,
        anchor_terms=fingerprint["anchor_terms"],
        dominant_scripts=fingerprint["dominant_scripts"],
        displacement_mode=actual_mode,
        embedding_scorer=embedding_scorer,
    )
    return seed_packets, build_sampler_context(
        text,
        round_num,
        fingerprint,
        round_profile,
        actual_mode,
        embedding_model,
        displacement_note,
    )


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
    parser.add_argument(
        "--orchestrate",
        action="store_true",
        default=False,
        help="Output full execution manifest with agent prompts (JSON)",
    )
    parser.add_argument("--concern-summary", type=str, help="Natural-language concern summary")
    parser.add_argument("--concern-file", type=str, help="Path to concern summary file")
    parser.add_argument("--predicates", type=str, help="Predicate formalization string")
    parser.add_argument("--predicates-file", type=str, help="Path to predicates file")
    parser.add_argument("--stage-b-synthesis", type=str, help="Stage B synthesis output")
    parser.add_argument("--stage-b-file", type=str, help="Path to Stage B synthesis file")
    parser.add_argument(
        "--displacement-mode",
        choices=["lexical", "embedding", "hybrid", "auto"],
        default="lexical",
        help="How aggressively to push tokens away from the artifact's default lexical space.",
    )
    parser.add_argument(
        "--embedding-model",
        type=str,
        default=DEFAULT_EMBEDDING_MODEL,
        help="Hugging Face model name used for semantic displacement when enabled.",
    )

    args = parser.parse_args()

    artifact = args.artifact
    if args.artifact_file:
        artifact = Path(args.artifact_file).read_text()
    if not artifact:
        parser.error("Provide --artifact or --artifact-file")

    token_catalog = load_tokenizer()

    if args.orchestrate:
        concern = args.concern_summary
        if args.concern_file:
            concern = Path(args.concern_file).read_text()
        if not concern:
            parser.error("--orchestrate requires --concern-summary or --concern-file")

        predicates = args.predicates
        if args.predicates_file:
            predicates = Path(args.predicates_file).read_text()
        if not predicates:
            parser.error("--orchestrate requires --predicates or --predicates-file")

        stage_b = args.stage_b_synthesis or ""
        if args.stage_b_file:
            stage_b = Path(args.stage_b_file).read_text()

        round_num = args.round if args.round is not None else 1
        seed_packets, sampler_context = generate_seed_packets(
            artifact,
            token_catalog,
            round_num,
            args.seeds,
            args.tokens,
            displacement_mode=args.displacement_mode,
            embedding_model=args.embedding_model,
        )

        persist_inputs(artifact, concern, predicates, stage_b)

        script_path = "${CLAUDE_SKILL_DIR}/perturb.py"
        manifest = build_manifest(
            seed_packets,
            concern,
            predicates,
            stage_b,
            round_num,
            script_path,
            sampler_context,
        )
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
        return

    if args.round is not None:
        seed_packets, sampler_context = generate_seed_packets(
            artifact,
            token_catalog,
            args.round,
            args.seeds,
            args.tokens,
            displacement_mode=args.displacement_mode,
            embedding_model=args.embedding_model,
        )
        print(json.dumps({
            "round": args.round,
            "strategy": sampler_context["round_strategy"],
            "anchor_terms": sampler_context["artifact_anchor_terms"],
            "dominant_scripts": sampler_context["artifact_dominant_scripts"],
            "displacement_mode": sampler_context["displacement_mode"],
            "seeds": {seed_id: packet["tokens"] for seed_id, packet in seed_packets.items()},
        }, ensure_ascii=False, indent=2))
    else:
        for offset in range(args.rounds):
            round_num = offset + 1
            seed_packets, sampler_context = generate_seed_packets(
                artifact,
                token_catalog,
                round_num,
                args.seeds,
                args.tokens,
                displacement_mode=args.displacement_mode,
                embedding_model=args.embedding_model,
            )
            print(json.dumps({
                "round": round_num,
                "strategy": sampler_context["round_strategy"],
                "anchor_terms": sampler_context["artifact_anchor_terms"],
                "dominant_scripts": sampler_context["artifact_dominant_scripts"],
                "displacement_mode": sampler_context["displacement_mode"],
                "seeds": {seed_id: packet["tokens"] for seed_id, packet in seed_packets.items()},
            }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
