#!/usr/bin/env python3
"""Create an allowlisted source-only snapshot from a pinned Git commit. No Docker/network.

No checkout mutation, no shell calls, no copying from working tree. Fails closed.
"""
from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import tempfile

COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
# Mandatory hard-coded exclusions cannot be weakened by editing source_policy.json.
HARD_DENIED_ROOTS = {"data", "datasets", "tests", "reports", "docs", "experiments", ".github", "audit"}
HARD_DENIED_SUFFIXES = {".pdf", ".db", ".sqlite", ".sqlite3", ".wal", ".shm",
                        ".pem", ".key", ".p12", ".pfx", ".crt"}


class PreflightError(RuntimeError):
    pass


def git(repo: Path, *args: str) -> bytes:
    p = subprocess.run(["git", "-C", str(repo), *args], stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, check=False)
    if p.returncode != 0:
        raise PreflightError(f"Git operation failed: {args[0]}; exit={p.returncode}")
    return p.stdout


def allowed(path: str, policy: dict) -> bool:
    if not path or "\\" in path or "\n" in path or "\r" in path or "\x00" in path:
        return False
    pp = PurePosixPath(path)
    if pp.is_absolute() or any(part in (".", "..", "") for part in path.split("/")):
        return False
    if (pp.parts[0] in HARD_DENIED_ROOTS or pp.suffix.lower() in HARD_DENIED_SUFFIXES
            or any(part.lower() == ".env" or part.lower().startswith(".env.") for part in pp.parts)):
        return False
    if any(fnmatch.fnmatch(part.lower(), pattern.lower())
           for part in pp.parts for pattern in policy["denied_basename_patterns"]):
        return False
    if path in policy["allowed_exact_files"]:
        return True
    if len(pp.parts) < 2:
        return False
    return pp.parts[0] in policy["allowed_roots"] and pp.suffix in policy["allowed_roots"][pp.parts[0]]


def make_source(repo: Path, sha: str, out: Path, policy_path: Path) -> dict:
    repo = repo.resolve()
    out = out.resolve()
    if not repo.is_dir():
        raise PreflightError("Repository directory not found")
    if not COMMIT_RE.fullmatch(sha):
        raise PreflightError("A full, lower-case 40-hex commit SHA is required")
    if out == repo or repo in out.parents or out in repo.parents:
        raise PreflightError("Output must be separate from the repository and its parents")
    if out.exists() or not out.parent.is_dir():
        raise PreflightError("Output must not exist; parent must exist")
    actual = git(repo, "rev-parse", "--verify", f"{sha}^{{commit}}").decode().strip()
    if actual != sha:
        raise PreflightError("Pinned SHA did not resolve to identical commit")
    tree = git(repo, "rev-parse", f"{sha}^{{tree}}").decode().strip()
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    entries = []
    for row in git(repo, "ls-tree", "-r", "-z", "--full-tree", sha).split(b"\0"):
        if not row:
            continue
        try:
            head, raw_path = row.split(b"\t", 1)
            mode, kind, obj = head.decode("ascii").split()
            path = raw_path.decode("utf-8", "strict")
        except (UnicodeDecodeError, ValueError) as exc:
            raise PreflightError("Unexpected Git tree encoding") from exc
        if allowed(path, policy):
            if mode not in ("100644", "100755") or kind != "blob":
                raise PreflightError("Nonregular source file or symlink in allowlist")
            entries.append((path, mode, obj))
    if not entries or "pyproject.toml" not in [x[0] for x in entries]:
        raise PreflightError("Source selection empty or pyproject.toml missing")
    tmp = Path(tempfile.mkdtemp(prefix="audit-source-incomplete-", dir=out.parent))
    try:
        total = 0
        manifest_files = []
        for path, mode, obj in sorted(entries):
            size = int(git(repo, "cat-file", "-s", obj).decode())
            if size > policy["max_file_bytes"] or total + size > policy["max_total_bytes"]:
                raise PreflightError("Source selection exceeds size policy")
            data = git(repo, "cat-file", "blob", obj)
            if len(data) != size:
                raise PreflightError("Git blob length mismatch")
            target = tmp / "src" / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            # Do not preserve executable bits from code source in the build context.
            target.chmod(0o644)
            total += size
            manifest_files.append({"path": path, "sha256": hashlib.sha256(data).hexdigest(), "bytes": size,
                                   "git_blob": obj, "git_mode": mode})
        dockerfile_data = Path(__file__).with_name("Dockerfile.audit").read_bytes()
        dockerignore_data = Path(__file__).with_name(".dockerignore").read_bytes()
        (tmp / "Dockerfile.audit").write_bytes(dockerfile_data)
        (tmp / ".dockerignore").write_bytes(dockerignore_data)
        (tmp / "metadata").mkdir()
        provenance = {"schema_version": "1.0", "subject_commit_sha": sha,
                      "subject_tree_sha": tree, "dockerfile_sha256": hashlib.sha256(dockerfile_data).hexdigest(),
                      "dockerignore_sha256": hashlib.sha256(dockerignore_data).hexdigest(),
                      "source_policy_sha256": hashlib.sha256(policy_path.read_bytes()).hexdigest(),
                      "included_files": manifest_files, "included_count": len(manifest_files),
                      "included_total_bytes": total, "purpose": "I0-1 SOURCE SNAPSHOT ONLY; NO BUILD OR RUN"}
        (tmp / "metadata" / "source_manifest.json").write_text(
            json.dumps(provenance, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        os.rename(tmp, out)
        return provenance
    except BaseException:
        shutil.rmtree(tmp, ignore_errors=True)
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--policy", type=Path, default=Path(__file__).with_name("source_policy.json"))
    a = parser.parse_args()
    try:
        p = make_source(a.repo, a.commit, a.out, a.policy)
    except (PreflightError, OSError, ValueError) as exc:
        parser.exit(2, f"SOURCE_PREPARE_FAILED: {exc}\n")
    print(f"SOURCE_PREPARED commit={p['subject_commit_sha']} tree={p['subject_tree_sha']} files={p['included_count']} bytes={p['included_total_bytes']}")
    print("NOT A BUILD, SECURITY CERTIFICATION OR E2E RESULT")


if __name__ == "__main__":
    main()
