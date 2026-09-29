#!/usr/bin/env python3
"""An optional append-only research record, not an agent or evidence verifier.

Usage:
  research_archive.py init ROOT --brief BRIEF.json
  research_archive.py add ROOT --node NODE.json
  research_archive.py packet ROOT --ids ID [ID ...]

ROOT contains brief.json, nodes/ID.json, and user-supplied artifact files.
Packets include selected records, all ancestors, and current artifact integrity,
never artifact contents. Each artifact receives a SHA-256 at add time; a supplied
sha256 must match. Integrity statuses are unchanged, changed, missing, unreadable.
Evidence labels are the author's claims. Artifacts are hashed, never executed or
frozen; their paths must name existing regular files inside ROOT at add time.
Complete records are published atomically without replacing existing records.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PureWindowsPath
import re
import stat
import tempfile
from typing import Any


KINDS = {"proposed", "observed", "bounded-check", "proved", "refuted"}


def _text(value: Any, field: str, *, empty: bool = False) -> str:
    if not isinstance(value, str) or (not empty and not value.strip()):
        raise ValueError(f"{field} must be a {'string' if empty else 'nonempty string'}")
    return value


def _id(value: Any) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", value):
        raise ValueError("ids must contain only letters, digits, underscores, or hyphens")
    return value


def _list(value: Any, field: str) -> list:
    if not isinstance(value, list):
        raise ValueError(f"{field} must be an array")
    return value


def _object(value: Any, field: str) -> dict:
    if not isinstance(value, dict):
        raise ValueError(f"{field} must be an object")
    return value


def _strings(value: Any, field: str) -> None:
    for item in _list(value, field):
        _text(item, field)


def _inside(root: Path, value: Any) -> Path:
    value = _text(value, "path")
    relative = Path(value)
    if relative.is_absolute() or ".." in relative.parts or "\\" in value or PureWindowsPath(value).drive:
        raise ValueError("paths must be relative to ROOT without parent traversal")
    resolved = (root / relative).resolve()
    if not resolved.is_relative_to(root):
        raise ValueError("path resolves outside ROOT")
    # Keep the named destination: resolving it here could bypass a dangling
    # symlink collision when publishing a create-only record.
    return root / relative


def _read(path: Path) -> dict:
    return _object(json.loads(path.read_text(encoding="utf-8")), str(path))


def _digest(path: Path) -> str:
    before = path.stat()
    if not stat.S_ISREG(before.st_mode):
        raise ValueError("artifact path must name a regular file")
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(65536), b""):
            digest.update(block)
        after = os.fstat(stream.fileno())
    signature = lambda value: (value.st_dev, value.st_ino, value.st_size,
                               value.st_mtime_ns, value.st_ctime_ns)
    if signature(before) != signature(after) or signature(after) != signature(path.stat()):
        raise ValueError("artifact changed while hashing; retry after writes finish")
    return digest.hexdigest()


def _integrity(root: Path, node_id: str, artifact: dict) -> dict:
    result = {"node_id": node_id, "path": artifact["path"],
              "recorded_sha256": artifact.get("sha256"), "current_sha256": None}
    try:
        if not isinstance(result["recorded_sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", result["recorded_sha256"]):
            raise ValueError("record has no valid SHA-256; its artifact version is unknown")
        result["current_sha256"] = _digest(_inside(root, artifact["path"]))
        result["status"] = "unchanged" if result["current_sha256"] == result["recorded_sha256"] else "changed"
    except FileNotFoundError:
        result["status"] = "missing"
    except (OSError, ValueError, RuntimeError) as exc:
        result.update(status="unreadable", error=str(exc))
    return result


def _publish(path: Path, record: dict) -> None:
    encoded = json.dumps(record, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix=".pending-", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        # A same-filesystem hard link publishes complete bytes and fails on collision.
        os.link(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def _validate_brief(brief: Any) -> dict:
    brief = _object(brief, "brief")
    _id(brief.get("id"))
    for field in ("objective", "domain", "source"):
        _text(brief.get(field), field)
    _strings(brief.get("constraints"), "constraints")
    return brief


def init_archive(root: Path, brief: Any) -> None:
    brief = _validate_brief(brief)
    root = Path(root).resolve()
    root.mkdir(parents=True, exist_ok=True)
    _inside(root, "nodes").mkdir(exist_ok=True)
    _publish(_inside(root, "brief.json"), brief)


def _node(root: Path, node_id: str, target_id: str) -> dict:
    record = _read(_inside(root, f"nodes/{_id(node_id)}.json"))
    if record.get("id") != node_id or record.get("target_id") != target_id:
        raise ValueError(f"node {node_id} has inconsistent identity or target")
    for parent in _list(record.get("parents"), "parents"):
        _id(parent)
    return record


def add_node(root: Path, node: Any) -> None:
    root = Path(root).resolve()
    brief = _validate_brief(_read(_inside(root, "brief.json")))
    node = dict(_object(node, "node"))
    node_id = _id(node.get("id"))
    if node.get("target_id") != brief["id"]:
        raise ValueError("target_id must match the brief id")
    for parent in _list(node.get("parents"), "parents"):
        _node(root, _id(parent), brief["id"])
    for field in ("representation", "operation", "next"):
        _text(node.get(field), field)
    for field in ("obstruction", "return_obligation"):
        _text(node.get(field), field, empty=True)
    _strings(node.get("assumptions"), "assumptions")
    artifacts = []
    for artifact in _list(node.get("artifacts"), "artifacts"):
        artifact = dict(_object(artifact, "artifact"))
        _text(artifact.get("description"), "artifact.description")
        digest = _digest(_inside(root, artifact.get("path")))
        if "sha256" in artifact and artifact["sha256"] != digest:
            raise ValueError("artifact.sha256 does not match the current file")
        artifacts.append({**artifact, "sha256": digest})
    node["artifacts"] = artifacts
    for evidence in _list(node.get("evidence"), "evidence"):
        evidence = _object(evidence, "evidence")
        if _text(evidence.get("kind"), "evidence.kind") not in KINDS:
            raise ValueError(f"evidence.kind must be one of {', '.join(sorted(KINDS))}")
        for field in ("claim", "source"):
            _text(evidence.get(field), f"evidence.{field}")
    _publish(_inside(root, f"nodes/{node_id}.json"), node)


def packet(root: Path, ids: list[str]) -> dict:
    root = Path(root).resolve()
    brief = _validate_brief(_read(_inside(root, "brief.json")))
    selected = list(dict.fromkeys(_id(item) for item in ids))
    if not selected:
        raise ValueError("at least one node id is required")
    records, seen, active = [], set(), set()
    stack = [(node_id, None) for node_id in reversed(selected)]
    while stack:
        node_id, record = stack.pop()
        if record is not None:
            active.remove(node_id)
            seen.add(node_id)
            records.append(record)
        elif node_id not in seen:
            if node_id in active:
                raise ValueError("cycle in archived ancestry")
            record = _node(root, node_id, brief["id"])
            active.add(node_id)
            stack.append((node_id, record))
            stack.extend((parent, None) for parent in reversed(record["parents"]))
    integrity = [_integrity(root, record["id"], artifact)
                 for record in records for artifact in record["artifacts"]]
    return {"brief": brief, "selected_ids": selected, "nodes": records,
            "artifact_integrity": integrity}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    for command, option in (("init", "brief"), ("add", "node"), ("packet", "ids")):
        subparser = commands.add_parser(command)
        subparser.add_argument("root", type=Path)
        if option == "ids":
            subparser.add_argument("--ids", nargs="+", required=True)
        else:
            subparser.add_argument(f"--{option}", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "packet":
            result = packet(args.root, args.ids)
        else:
            record = _read(getattr(args, "brief" if args.command == "init" else "node"))
            (init_archive if args.command == "init" else add_node)(args.root, record)
            result = {"created": "brief" if args.command == "init" else "node", "id": record["id"]}
        print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
    except (OSError, ValueError, RuntimeError) as exc:
        parser.exit(2, f"research_archive: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
