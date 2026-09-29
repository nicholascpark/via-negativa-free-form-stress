#!/usr/bin/env python3
"""Build the inspectable fixture using a locally downloaded TinyCLIP checkpoint.

Requires torch, transformers, numpy, Pillow, and scikit-learn's sample photos.
No downloads or network calls. The input corpus is deliberately small and curated;
this demonstrates geometry and sampling, not creative effectiveness.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil

import numpy as np
from PIL import Image
import sklearn
import torch
import transformers
from transformers import CLIPModel, CLIPProcessor

from semantic_walk import run_walks

MODEL_ID = "wkcn/TinyCLIP-ViT-8M-16-Text-3M-YFCC15M"
REVISION = "a2a8c6eaa2549ad66eb7c31b85022bf58273a26c"
CHECKPOINT_HASHES = {
    "config.json": "c586d856dbd5589b67525db9e791ee0917402405672c7773aead373efb7d7bca",
    "preprocessor_config.json": "910e70b3956ac9879ebc90b22fb3bc8a75b6a0677814500101a4c072bd7857bd",
    "tokenizer.json": "b556ac8c99757ffb677208af34bc8c6721572114111a6e0aaf5fa69ff0b8d842",
    "model.safetensors": "9339ee3d736344d0ddcaa6c03edc9f89688f08caaea5401220885233da726fcc",
}
TEXTS = [
    ("queue", "A queue of people waiting for service at a counter."),
    ("echo", "An echo repeats the same sound across a valley."),
    ("relay", "A relay passes a message from one station to another."),
    ("lease", "A lease grants temporary use and then expires."),
    ("branch", "A tree branch splits into smaller branches."),
    ("fold", "A sheet of paper folded into overlapping layers."),
    ("reservoir", "A reservoir stores water and releases it when needed."),
    ("broadcast", "One speaker broadcasts an announcement to many listeners."),
    ("festival", "A festival brings many visitors to a shared public square."),
    ("reflection", "A reflection of a building appears on the surface of water."),
    ("tide", "The tide repeatedly fills and empties a shallow inlet."),
    ("germination", "A seed germinates when moisture and temperature permit growth."),
    ("bottleneck", "Many vehicles converge at a narrow bridge."),
    ("lattice", "A lattice connects many crossing strips into a supporting structure."),
    ("horizon", "The horizon separates the visible sky from the distant sea."),
    ("partition", "A wall divides one room into separate private spaces."),
    ("renewal", "An expiring agreement is renewed after checking its conditions."),
    ("rotation", "Workers rotate duties so one person does not carry every task."),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-path", type=Path, required=True,
                        help="Local snapshot of the pinned TinyCLIP revision")
    parser.add_argument("--output-dir", type=Path,
                        default=Path(__file__).resolve().parents[1] / "examples/semantic-exploration")
    args = parser.parse_args()
    checkpoint = args.model_path.resolve()
    # Pin the actual files too; a revision label by itself is not verification.
    hashes = {}
    for name in ("config.json", "preprocessor_config.json", "tokenizer.json", "model.safetensors"):
        hashes[name] = hashlib.sha256((checkpoint / name).read_bytes()).hexdigest()
    if hashes != CHECKPOINT_HASHES:
        raise ValueError("Local files do not match the pinned demonstration checkpoint")
    model = CLIPModel.from_pretrained(checkpoint, local_files_only=True,
                                      use_safetensors=True).eval()
    processor = CLIPProcessor.from_pretrained(checkpoint, local_files_only=True)
    output = args.output_dir.resolve()
    (output / "images").mkdir(parents=True, exist_ok=True)
    photos = Path(sklearn.__file__).parent / "datasets/images"
    for name in ("china.jpg", "flower.jpg", "README.txt"):
        shutil.copyfile(photos / name, output / "images" / name)
    objective = {
        "id": "objective",
        "text": "Reduce latency for a burst of identical product requests while preserving tenant isolation and one-second data freshness.",
        "status": "Illustrative task; no product or user outcome was measured.",
    }
    cues = [{"id": label, "label": label, "kind": "text", "text": text,
             "source": "Curated demonstration corpus in scripts/build_semantic_demo.py"}
            for label, text in TEXTS]
    image_cues = [
        {"id": "pavilion", "label": "Pavilion beside water", "image": "images/china.jpg"},
        {"id": "flower", "label": "Flower with layered petals", "image": "images/flower.jpg"},
    ]
    texts = [objective["text"], *(cue["text"] for cue in cues)]
    encoded_text = processor(text=texts, padding=True, return_tensors="pt")
    if encoded_text["input_ids"].shape[1] > model.config.text_config.max_position_embeddings:
        raise ValueError("Fixture text exceeds the encoder's token budget; do not silently truncate")
    images = [Image.open(output / cue["image"]).convert("RGB") for cue in image_cues]
    with torch.inference_mode():
        text_vectors = model.get_text_features(**encoded_text).cpu().numpy()
        image_vectors = model.get_image_features(**processor(images=images, return_tensors="pt")).cpu().numpy()
    vectors = np.concatenate([text_vectors, image_vectors]).astype(np.float64)
    if not np.isfinite(vectors).all() or np.any(np.linalg.norm(vectors, axis=1) == 0):
        raise ValueError("Encoder returned invalid vectors")
    vectors /= np.linalg.norm(vectors, axis=1, keepdims=True)
    objective["embedding"] = vectors[0].tolist()
    for i, cue in enumerate(cues, 1):
        cue["embedding"] = vectors[i].tolist()
    for i, cue in enumerate(image_cues, len(cues) + 1):
        cue.update(kind="image", source="scikit-learn sample photos; original licence and credits in images/README.txt",
                   input_sha256=hashlib.sha256((output / cue["image"]).read_bytes()).hexdigest(),
                   embedding=vectors[i].tolist())
        cues.append(cue)
    encoder = {"id": MODEL_ID, "revision": REVISION, "dimension": vectors.shape[1]}
    payload = {"encoder": encoder, "objective": objective, "cues": cues,
               "operators": ["invert a relation", "change scale", "share a resource", "separate roles", "change timing"]}
    (output / "input.json").write_text(json.dumps(payload, indent=2) + "\n")
    centered = vectors - vectors.mean(axis=0)
    u, singular, _ = np.linalg.svd(centered, full_matrices=False)
    xy = u[:, :2] * singular[:2]
    data = dict(payload)
    data["provenance"] = {"checkpoint_sha256": hashes, "torch": torch.__version__,
                          "transformers": transformers.__version__, "numpy": np.__version__,
                          "note": "Text encoded from exact text fields; images encoded from pixels, not labels. CPU inference. Cached vectors included; no API needed to inspect."}
    data["projection"] = {"method": "PCA on centered normalized joint embeddings",
                          "points": [{"id": item["id"], "x": float(x), "y": float(y)}
                                     for item, (x, y) in zip([objective, *cues], xy)],
                          "explained_variance": (singular[:2] ** 2 / np.sum(singular ** 2)).tolist()}
    data["runs"] = [run_walks(payload, seed=seed, walks=3, hops=3) for seed in (1, 7, 42)]
    bridge_path = Path(__file__).resolve().parents[1] / "experiments/semantic-walk/bridge_example.py"
    spec = importlib.util.spec_from_file_location("bridge_example", bridge_path)
    bridge_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bridge_module)
    data["bridge"] = bridge_module.generate()
    (output / "data.json").write_text(json.dumps(data, indent=2) + "\n")
    print(json.dumps({"output": str(output), "dimension": vectors.shape[1], "text_cues": len(TEXTS),
                      "image_cues": len(image_cues), "seeds": [1, 7, 42],
                      "pca_variance_retained": float(sum(data["projection"]["explained_variance"]))}, indent=2))


if __name__ == "__main__":
    main()
