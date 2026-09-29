"""Archive integrity checks; these do not verify recorded research claims."""

from concurrent.futures import ThreadPoolExecutor
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest


SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "research_archive.py"
sys.dont_write_bytecode = True
SPEC = importlib.util.spec_from_file_location("research_archive", SCRIPT)
archive = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(archive)


def node(node_id="start", parents=None):
    return {"id": node_id, "target_id": "goal", "parents": parents or [],
            "representation": "A finite transition model", "operation": "derive",
            "artifacts": [{"path": "model.txt", "description": "Unverified model"}],
            "assumptions": [], "obstruction": "", "return_obligation": "",
            "evidence": [{"kind": "proposed", "claim": "A candidate invariant", "source": "author"}],
            "next": "Try a counterexample", "extra_metadata": {"worker": "one"}}


class ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "archive"
        self.brief = {"id": "goal", "objective": "Investigate a mechanism", "constraints": [],
                      "domain": "engineering", "source": "test", "extra_metadata": [1, 2]}
        archive.init_archive(self.root, self.brief)
        (self.root / "model.txt").write_text("Never include this file's contents in a packet.")

    def recorded(self, record):
        result = copy.deepcopy(record)
        for artifact in result["artifacts"]:
            artifact["sha256"] = hashlib.sha256((self.root / artifact["path"]).read_bytes()).hexdigest()
        return result

    def test_records_are_create_only_and_preserve_metadata(self):
        original = node()
        archive.add_node(self.root, original)
        changed = copy.deepcopy(original)
        changed["representation"] = "An attempted replacement"
        with self.assertRaises(FileExistsError):
            archive.add_node(self.root, changed)
        with self.assertRaises(FileExistsError):
            archive.init_archive(self.root, {**self.brief, "objective": "replacement"})
        result = archive.packet(self.root, ["start"])
        self.assertEqual(result["brief"], self.brief)
        self.assertEqual(result["selected_ids"], ["start"])
        self.assertEqual(result["nodes"], [self.recorded(original)])
        self.assertNotIn("sha256", original["artifacts"][0])
        self.assertEqual(list(self.root.rglob(".pending-*")), [])

    def test_invalid_target_parent_and_ids_cannot_publish(self):
        changes = [{"target_id": "other"}, {"parents": ["missing"]},
                   {"id": "../escape"}, {"id": "/absolute"}, {"id": ""},
                   {"parents": ["../outside"]}, {"representation": ""}]
        for change in changes:
            with self.subTest(change=change), self.assertRaises((ValueError, OSError)):
                archive.add_node(self.root, {**node(), **change})
        self.assertEqual(list((self.root / "nodes").iterdir()), [])

    def test_dangling_record_symlink_is_still_a_collision(self):
        destination = self.root / "unrelated.json"
        (self.root / "nodes" / "start.json").symlink_to(destination)
        with self.assertRaises(FileExistsError):
            archive.add_node(self.root, node())
        self.assertFalse(destination.exists())

    def test_artifact_paths_reject_escape_missing_and_directories(self):
        outside = Path(self.temp.name) / "outside.txt"
        outside.write_text("external")
        (self.root / "escape").symlink_to(outside)
        for path in (str(outside), "../outside.txt", "escape", "missing", "nodes", "C:\\outside.txt"):
            candidate = node()
            candidate["artifacts"][0]["path"] = path
            with self.subTest(path=path), self.assertRaises((ValueError, OSError)):
                archive.add_node(self.root, candidate)
        (self.root / "internal").symlink_to(self.root / "model.txt")
        candidate["artifacts"][0]["path"] = "internal"
        archive.add_node(self.root, candidate)

    def test_packet_is_ancestry_snapshot_without_artifact_contents(self):
        expected = [node("base"), node("left", ["base"]), node("right", ["base"]),
                    node("join", ["left", "right"])]
        for record in expected:
            archive.add_node(self.root, record)
        result = archive.packet(self.root, ["join", "left", "join"])
        self.assertEqual(result["brief"], self.brief)
        self.assertEqual(result["selected_ids"], ["join", "left"])
        self.assertEqual(result["nodes"], [self.recorded(record) for record in expected])
        archive.add_node(self.root, node("later", ["join"]))
        self.assertEqual(archive.packet(self.root, ["join", "left"]), result)
        self.assertNotIn("Never include", json.dumps(result))
        # Historical records stay unchanged while current integrity changes.
        (self.root / "model.txt").unlink()
        missing = archive.packet(self.root, ["join", "left"])
        self.assertEqual(missing["nodes"], result["nodes"])
        self.assertTrue(all(item["status"] == "missing" for item in missing["artifact_integrity"]))

    def test_concurrent_duplicate_has_exactly_one_complete_winner(self):
        barrier = threading.Barrier(8)

        def publish(index):
            record = node("contested")
            record["writer"] = index
            barrier.wait()
            try:
                archive.add_node(self.root, record)
                return record
            except FileExistsError:
                return None

        with ThreadPoolExecutor(max_workers=8) as pool:
            winners = [result for result in pool.map(publish, range(8)) if result is not None]
        self.assertEqual(len(winners), 1)
        self.assertEqual(archive.packet(self.root, ["contested"])["nodes"], [self.recorded(winners[0])])
        self.assertEqual(list(self.root.rglob(".pending-*")), [])

    def test_evidence_labels_are_validated_but_not_attested(self):
        candidate = node()
        candidate["evidence"][0]["kind"] = "certain"
        with self.assertRaises(ValueError):
            archive.add_node(self.root, candidate)
        candidate["evidence"][0]["kind"] = "proved"
        archive.add_node(self.root, candidate)
        self.assertEqual(archive.packet(self.root, ["start"])["nodes"][0], self.recorded(candidate))

    def test_artifact_drift_preserves_historical_versions(self):
        archive.add_node(self.root, node("old"))
        original = archive.packet(self.root, ["old"])
        old_hash = original["nodes"][0]["artifacts"][0]["sha256"]
        self.assertEqual(original["artifact_integrity"], [{"node_id": "old", "path": "model.txt",
                         "recorded_sha256": old_hash, "current_sha256": old_hash, "status": "unchanged"}])
        (self.root / "model.txt").write_bytes(b"A different artifact version")
        new_hash = hashlib.sha256(b"A different artifact version").hexdigest()
        archive.add_node(self.root, node("new", ["old"]))
        result = archive.packet(self.root, ["new"])
        self.assertEqual(result["nodes"][0], original["nodes"][0])
        self.assertEqual(result["artifact_integrity"], [
            {"node_id": "old", "path": "model.txt", "recorded_sha256": old_hash,
             "current_sha256": new_hash, "status": "changed"},
            {"node_id": "new", "path": "model.txt", "recorded_sha256": new_hash,
             "current_sha256": new_hash, "status": "unchanged"}])
        self.assertNotIn("A different artifact version", json.dumps(result))
        (self.root / "model.txt").unlink()
        missing = archive.packet(self.root, ["new"])
        self.assertEqual(missing["nodes"], result["nodes"])
        self.assertTrue(all(item["status"] == "missing" and item["current_sha256"] is None
                            for item in missing["artifact_integrity"]))

    def test_supplied_digest_must_match_before_publication(self):
        candidate = node()
        candidate["artifacts"][0]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "sha256 does not match"):
            archive.add_node(self.root, candidate)
        self.assertFalse((self.root / "nodes" / "start.json").exists())
        candidate = self.recorded(candidate)
        archive.add_node(self.root, candidate)
        self.assertEqual(archive.packet(self.root, ["start"])["nodes"], [candidate])

    def test_unreadable_artifacts_are_reported_without_losing_records(self):
        archive.add_node(self.root, node())
        recorded = archive.packet(self.root, ["start"])["nodes"]
        artifact = self.root / "model.txt"
        artifact.unlink()
        artifact.mkdir()
        result = archive.packet(self.root, ["start"])
        self.assertEqual(result["nodes"], recorded)
        self.assertEqual(result["artifact_integrity"][0]["status"], "unreadable")
        self.assertIsNone(result["artifact_integrity"][0]["current_sha256"])
        artifact.rmdir()
        outside = Path(self.temp.name) / "external.txt"
        outside.write_text("external contents must not be inspected")
        artifact.symlink_to(outside)
        result = archive.packet(self.root, ["start"])
        self.assertEqual(result["artifact_integrity"][0]["status"], "unreadable")
        self.assertIn("outside ROOT", result["artifact_integrity"][0]["error"])

    def test_cli_init_add_packet_and_error_exit(self):
        cli_root = Path(self.temp.name) / "cli-archive"
        for action, option, record in (("init", "brief", self.brief), ("add", "node", node())):
            source = Path(self.temp.name) / f"{option}-input.json"
            source.write_text(json.dumps(record))
            result = subprocess.run([sys.executable, str(SCRIPT), action, str(cli_root),
                                     f"--{option}", str(source)], text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout), {"created": option, "id": record["id"]})
            if action == "init":
                (cli_root / "model.txt").write_text("artifact")
        command = [sys.executable, str(SCRIPT), "packet", str(cli_root), "--ids"]
        success = subprocess.run(command + ["start"], text=True, capture_output=True)
        self.assertEqual(success.returncode, 0, success.stderr)
        self.assertEqual(json.loads(success.stdout), archive.packet(cli_root, ["start"]))
        failure = subprocess.run(command + ["../escape"], text=True, capture_output=True)
        self.assertEqual(failure.returncode, 2)
        self.assertEqual(failure.stdout, "")


if __name__ == "__main__":
    unittest.main()
