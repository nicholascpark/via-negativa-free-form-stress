"""Controller checks with synthetic geometry, never evidence of semantic benefit."""

import copy
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "semantic_walk.py"
SPEC = importlib.util.spec_from_file_location("semantic_walk", SCRIPT)
walk = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(walk)


def fixture(count=7):
    # Coordinates are deliberately synthetic unit-test fixtures, not embeddings.
    return {
        "encoder": {"id": "synthetic-test-geometry", "revision": "test-only", "dimension": 2},
        "objective": {"id": "goal", "text": "Synthetic geometry, not a semantic objective", "embedding": [2, 0]},
        "cues": [{"id": f"cue-{i}", "label": f"Synthetic point {i}", "kind": "text",
                  "source": "unit-test-only", "embedding": [math.cos(i * 0.4), math.sin(i * 0.4)]}
                 for i in range(count)],
        "operators": ["split", "change scale"],
    }


class SamplerTests(unittest.TestCase):
    def test_cosine_is_scale_invariant_even_at_extreme_magnitudes(self):
        self.assertAlmostEqual(walk.cosine_distance([1e308, 1e308], [1e-300, 1e-300]), 0)
        self.assertAlmostEqual(walk.cosine_distance([7, 0], [0, 91]), 1)
        self.assertAlmostEqual(walk.cosine_distance([7, 0], [-91, 0]), 2)
        self.assertAlmostEqual(sum(x * x for x in walk.normalize_embedding([3, 4])), 1)

    def test_rank_band_probabilities_and_small_pool_renormalization(self):
        for count in range(1, 14):
            data = walk.validate_input(fixture(count))
            distribution = walk.transition_distribution(data["objective"]["embedding"], data["cues"])
            self.assertAlmostEqual(sum(row["probability"] for row in distribution), 1)
            self.assertTrue(all(row["probability"] > 0 for row in distribution))
            self.assertEqual(len(distribution), count)
        data = walk.validate_input(fixture(7))
        rows = walk.transition_distribution(data["objective"]["embedding"], data["cues"])
        self.assertEqual([sum(row["band"] == band for row in rows) for band in walk.BANDS], [3, 2, 2])
        self.assertAlmostEqual(rows[0]["probability"], .2 / 3)
        self.assertAlmostEqual(rows[3]["probability"], .5 / 2)
        self.assertAlmostEqual(rows[5]["probability"], .3 / 2)
        rows = walk.transition_distribution([1, 0], data["cues"][:2])
        self.assertAlmostEqual(rows[0]["probability"], .2 / .7)
        self.assertAlmostEqual(rows[1]["probability"], .5 / .7)

    def test_draw_frequency_matches_declared_distribution(self):
        data = walk.validate_input(fixture(7))
        rows = walk.transition_distribution([1, 0], data["cues"])
        rng = walk.random.Random(32)
        counts = {row["cue_id"]: 0 for row in rows}
        trials = 30000
        for _ in range(trials):
            counts[walk._draw(rows, rng)["cue_id"]] += 1
        for row in rows:
            self.assertAlmostEqual(counts[row["cue_id"]] / trials, row["probability"], delta=.012)

    def test_modality_is_stratified_before_distance_not_confounded_with_it(self):
        payload = fixture(7)
        payload["cues"][-1]["kind"] = "image"
        data = walk.validate_input(payload)
        rows = walk.transition_distribution([1, 0], data["cues"])
        image = [row for row in rows if row["kind"] == "image"]
        text = [row for row in rows if row["kind"] == "text"]
        self.assertEqual(len(image), 1)
        self.assertAlmostEqual(image[0]["probability"], .5)
        self.assertAlmostEqual(sum(row["probability"] for row in text), .5)
        self.assertEqual(image[0]["band"], "near")  # Relative to its own modality.
        for row in rows:
            self.assertAlmostEqual(row["probability"],
                                   row["kind_probability"] * row["band_probability"] / row["band_size"])
        without_image = walk.transition_distribution([1, 0], data["cues"][:-1])
        self.assertAlmostEqual(sum(row["probability"] for row in without_image), 1)
        self.assertTrue(all(row["kind_probability"] == 1 for row in without_image))

    def test_reproducible_paths_preserve_lineage_probability_and_no_repeats(self):
        payload = fixture()
        untouched = copy.deepcopy(payload)
        result = walk.run_walks(payload, seed=41, walks=3, hops=9)
        self.assertEqual(payload, untouched)
        self.assertEqual(result, walk.run_walks(payload, seed=41, walks=3, hops=9))
        self.assertNotEqual(result["paths"], walk.run_walks(payload, seed=51, walks=3, hops=9)["paths"])
        data = walk.validate_input(payload)
        by_id = {item["id"]: item for item in [data["objective"], *data["cues"]]}
        archive = []
        for path in result["paths"]:
            self.assertEqual(path["termination"], "pool_exhausted")
            self.assertEqual(len(path["steps"]), 7)
            used = set()
            previous = "goal"
            for step in path["steps"]:
                self.assertEqual(step["previous_id"], previous)
                self.assertNotIn(step["current_id"], used)
                available = [cue for cue in data["cues"] if cue["id"] not in used]
                rows = walk.transition_distribution(by_id[previous]["embedding"], available)
                selected = next(row for row in rows if row["cue_id"] == step["current_id"])
                self.assertAlmostEqual(step["transition_probability"], selected["probability"])
                self.assertAlmostEqual(step["joint_probability"], selected["probability"] / 2)
                vector = by_id[step["current_id"]]["embedding"]
                expected_novelty = min((walk.cosine_distance(vector, by_id[item]["embedding"])
                                        for item in archive), default=None)
                self.assertEqual(step["min_distance_to_earlier_cues"], expected_novelty)
                archive.append(step["current_id"])
                used.add(step["current_id"])
                previous = step["current_id"]
        self.assertFalse(result["utility_assessed"])

    def test_empty_pool_is_an_honest_no_transition_result(self):
        result = walk.run_walks(fixture(0), seed=1)
        self.assertEqual(result["observed_hops"], 0)
        self.assertTrue(all(path["termination"] == "pool_exhausted" for path in result["paths"]))

    def test_reject_invalid_vectors_ids_and_missing_or_mixed_metadata(self):
        invalid = []
        for vector in ([0, 0], [1], [float("nan"), 1], [float("inf"), 1], [True, 1], ["1", 1]):
            payload = fixture()
            payload["cues"][0]["embedding"] = vector
            invalid.append(payload)
        payload = fixture()
        payload["cues"][0]["encoder"] = {**payload["encoder"], "revision": "different"}
        invalid.append(payload)
        payload = fixture()
        del payload["encoder"]["revision"]
        invalid.append(payload)
        payload = fixture()
        payload["cues"][0]["id"] = "goal"
        invalid.append(payload)
        payload = fixture()
        del payload["cues"][0]["source"]
        invalid.append(payload)
        for payload in invalid:
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                walk.run_walks(payload, seed=1)
        valid = fixture()
        valid["cues"][0]["encoder"] = dict(valid["encoder"])
        walk.run_walks(valid, seed=1)

    def test_custom_weights_and_bad_configuration(self):
        self.assertEqual(walk.validate_weights([1, 1, 1]), (1 / 3, 1 / 3, 1 / 3))
        for weights in ([0, 1, 1], [1, -1, 1], [1, 2], [1, float("inf"), 1]):
            with self.subTest(weights=weights), self.assertRaises(ValueError):
                walk.run_walks(fixture(), seed=1, weights=weights)
        for kwargs in ({"seed": True}, {"seed": 1, "hops": 0}, {"seed": 1, "walks": -2}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                walk.run_walks(fixture(), **kwargs)

    def test_cli_writes_result_and_rejects_overwriting_source(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "input.json"
            output = Path(directory) / "nested" / "result.json"
            source.write_text(json.dumps(fixture()), encoding="utf-8")
            process = subprocess.run([sys.executable, str(SCRIPT), str(source), "--seed", "17",
                                      "--output", str(output)], capture_output=True, text=True)
            self.assertEqual(process.returncode, 0, process.stderr)
            self.assertEqual(json.loads(output.read_text()), walk.run_walks(fixture(), seed=17))
            process = subprocess.run([sys.executable, str(SCRIPT), str(source), "--seed", "17",
                                      "--output", str(source)], capture_output=True, text=True)
            self.assertEqual(process.returncode, 2)
            self.assertEqual(json.loads(source.read_text()), fixture())


if __name__ == "__main__":
    unittest.main()
