#!/usr/bin/env python3
"""Fail-closed I0-1 materials verifier and offline-build-context assembler.

Does NOT download, install, build or execute anything. Materials must have been
obtained through a separately approved and logged acquisition procedure.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import tempfile
import tomllib

from prepare_source import PreflightError

SHA = re.compile(r"^[a-f0-9]{64}$")
IMAGE = re.compile(r"^[a-zA-Z0-9._:/-]+@sha256:[a-f0-9]{64}$")
FILE = re.compile(r"^(?:requirements\.lock|tectonic|wheels/[a-zA-Z0-9_.+\-]+\.whl)$")
PIN = re.compile(r"^([a-zA-Z][a-zA-Z0-9_.-]*)==([a-zA-Z0-9][a-zA-Z0-9_.+!\-]*)\b")
HASH = re.compile(r"--hash=sha256:([0-9a-f]{64})\b")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normal(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def require_regular(root: Path, rel: str) -> Path:
    target = root / rel
    if not target.is_file() or target.is_symlink():
        raise PreflightError(f"Required regular artifact not present: {rel}")
    if any(parent.is_symlink() for parent in target.parents if parent != root and root in parent.parents):
        raise PreflightError("Symlink directory not accepted")
    return target


def parse_lock(data: bytes) -> dict[str, tuple[str, set[str]]]:
    try:
        txt = data.decode("utf-8", "strict")
    except UnicodeDecodeError as exc:
        raise PreflightError("Lock is not UTF-8") from exc
    txt = txt.replace("\\\n", " ")
    pins = {}
    for line in txt.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        if s.startswith("-") or "git+" in s or "file:" in s or "https:" in s or "http:" in s:
            raise PreflightError("Unapproved lock option, include, URL or VCS source")
        # pip-compile may add trailing comments after hashes; strip them.
        s = s.split(" #", 1)[0]
        found = PIN.match(s)
        hashes = set(HASH.findall(s))
        if not found or not hashes:
            raise PreflightError("Every locked distribution must have an exact version and SHA-256 hash")
        name, version = normal(found.group(1)), found.group(2)
        remainder = s[found.end():]
        remainder = HASH.sub("", remainder).strip()
        if remainder and remainder not in (";",):
            raise PreflightError("Unsupported lock syntax; review generator output before continuing")
        if name in pins:
            raise PreflightError("Duplicate distribution in lock")
        pins[name] = (version, hashes)
    if not pins:
        raise PreflightError("Empty Python dependency lock")
    return pins


def verify(src_dir: Path, materials_dir: Path) -> dict:
    src_dir, materials_dir = src_dir.resolve(), materials_dir.resolve()
    if not src_dir.is_dir() or not materials_dir.is_dir():
        raise PreflightError("Source/material directory missing")
    src_manifest_path = require_regular(src_dir, "metadata/source_manifest.json")
    src_manifest = json.loads(src_manifest_path.read_text(encoding="utf-8"))
    if src_manifest.get("purpose") != "I0-1 SOURCE SNAPSHOT ONLY; NO BUILD OR RUN":
        raise PreflightError("Unknown source provenance schema")
    if src_manifest.get("source_policy_sha256") != digest(Path(__file__).with_name("source_policy.json").read_bytes()):
        raise PreflightError("Source policy differs from verified instrument version")
    if src_manifest.get("dockerfile_sha256") != digest(Path(__file__).with_name("Dockerfile.audit").read_bytes()):
        raise PreflightError("Dockerfile fingerprint differs from instrument version")
    if digest(require_regular(src_dir, "Dockerfile.audit").read_bytes()) != src_manifest["dockerfile_sha256"]:
        raise PreflightError("Snapshot Dockerfile has been changed")
    dockerignore = Path(__file__).with_name(".dockerignore").read_bytes()
    if src_manifest.get("dockerignore_sha256") != digest(dockerignore):
        raise PreflightError("Docker context exclusion policy fingerprint mismatch")
    if digest(require_regular(src_dir, ".dockerignore").read_bytes()) != digest(dockerignore):
        raise PreflightError("Source Docker context exclusion policy was modified")
    for entry in (src_dir / "src").rglob("*"):
        if entry.is_symlink():
            raise PreflightError("Symlink found in staged source tree")
    files = src_manifest.get("included_files", [])
    if not files or not isinstance(files, list):
        raise PreflightError("Source manifest has no files")
    if len(files) != src_manifest.get("included_count"):
        raise PreflightError("Source manifest count mismatch")
    listed = set()
    for obj in files:
        path, expected = obj["path"], obj["sha256"]
        if path in listed or not SHA.fullmatch(expected):
            raise PreflightError("Duplicate or invalid source manifest entry")
        listed.add(path)
        pp = PurePosixPath(path)
        if pp.is_absolute() or ".." in pp.parts or "\\" in path:
            raise PreflightError("Unsafe source manifest path")
        data = require_regular(src_dir, "src/" + path).read_bytes()
        if digest(data) != expected or len(data) != obj["bytes"]:
            raise PreflightError("Source file does not match pinned manifest")
    actual_src = {p.relative_to(src_dir / "src").as_posix() for p in (src_dir / "src").rglob("*") if p.is_file()}
    if actual_src != listed:
        raise PreflightError("Unlisted/missing file in source snapshot")
    manifest = json.loads(require_regular(materials_dir, "materials-manifest.json").read_text(encoding="utf-8"))
    if manifest.get("schema_version") != "1.0" or manifest.get("status") != "APPROVED_MATERIALS":
        raise PreflightError("Materials manifest is not approved/complete")
    if manifest.get("target_platform") != "linux/amd64" or manifest.get("python_version") != "3.11":
        raise PreflightError("Unexpected runtime platform")
    if manifest.get("groq_version") != "1.4.0":
        raise PreflightError("Groq SDK version differs from preregistered contract")
    if not isinstance(manifest.get("base_image"), str) or not IMAGE.fullmatch(manifest["base_image"]):
        raise PreflightError("Base image must have an exact sha256 digest")
    expected_files = manifest.get("files")
    if not isinstance(expected_files, dict):
        raise PreflightError("Material file hash map missing")
    if not {"requirements.lock", "tectonic"}.issubset(expected_files):
        raise PreflightError("Required artifacts not listed")
    if not any(k.startswith("wheels/") for k in expected_files):
        raise PreflightError("No wheels listed")
    actual_files = {p.relative_to(materials_dir).as_posix()
                    for p in materials_dir.rglob("*") if p.is_file()}
    if actual_files != set(expected_files) | {"materials-manifest.json"}:
        raise PreflightError("Unexpected, missing or unlisted material (including possible secret)")
    data_by_file = {}
    for rel, expected in expected_files.items():
        if not FILE.fullmatch(rel) or not isinstance(expected, str) or not SHA.fullmatch(expected):
            raise PreflightError("Unsafe filename or invalid/missing SHA-256")
        blob = require_regular(materials_dir, rel).read_bytes()
        if digest(blob) != expected:
            raise PreflightError("Artifact SHA-256 mismatch")
        data_by_file[rel] = blob
    pins = parse_lock(data_by_file["requirements.lock"])
    if pins.get("groq", (None,))[0] != "1.4.0":
        raise PreflightError("groq==1.4.0 absent from dependency lock")
    project = tomllib.loads(require_regular(src_dir, "src/pyproject.toml").read_text(encoding="utf-8"))
    for req in project.get("project", {}).get("dependencies", []):
        match = re.match(r"^([a-zA-Z][a-zA-Z0-9_.-]*)", req)
        if not match or normal(match.group(1)) not in pins:
            raise PreflightError("Project direct dependency not represented in locked wheelhouse")
    matched_packages = set()
    for rel, data in data_by_file.items():
        if not rel.startswith("wheels/"):
            continue
        wheel = rel.split("/", 1)[1]
        parts = wheel.removesuffix(".whl").split("-")
        if len(parts) < 5:
            raise PreflightError("Invalid wheel filename")
        name, version = normal(parts[0]), parts[1]
        if name not in pins or pins[name][0] != version or digest(data) not in pins[name][1]:
            raise PreflightError("Wheel does not match exact package/version/lock SHA")
        if "win" in wheel.lower() or "macosx" in wheel.lower():
            raise PreflightError("Non-Linux wheel supplied")
        if name in matched_packages:
            raise PreflightError("Ambiguous multiple wheels for one package")
        matched_packages.add(name)
    if matched_packages != set(pins):
        raise PreflightError("Wheelhouse is incomplete or has extra distributions")
    return {"source_manifest_sha256": digest(src_manifest_path.read_bytes()),
            "materials_manifest_sha256": digest(require_regular(materials_dir, "materials-manifest.json").read_bytes()),
            "subject_commit_sha": src_manifest["subject_commit_sha"],
            "subject_tree_sha": src_manifest["subject_tree_sha"],
            "base_image": manifest["base_image"],
            "target_platform": manifest["target_platform"],
            "locked_distribution_count": len(pins),
            "wheel_count": len(matched_packages),
            "state": "STATIC_MATERIALS_VERIFIED_NOT_BUILT"}


def assemble(src_dir: Path, materials_dir: Path, out: Path) -> dict:
    src_dir, materials_dir, out = src_dir.resolve(), materials_dir.resolve(), out.resolve()
    if out.exists() or not out.parent.is_dir():
        raise PreflightError("New output directory with existing parent required")
    if any(out == p or p in out.parents or out in p.parents for p in (src_dir, materials_dir)):
        raise PreflightError("Output must be separate from source and materials trees")
    result = verify(src_dir, materials_dir)
    temp = Path(tempfile.mkdtemp(prefix="audit-build-incomplete-", dir=out.parent))
    try:
        shutil.copytree(src_dir / "src", temp / "src")
        shutil.copyfile(require_regular(src_dir, "Dockerfile.audit"), temp / "Dockerfile.audit")
        shutil.copyfile(require_regular(src_dir, ".dockerignore"), temp / ".dockerignore")
        shutil.copyfile(materials_dir / "requirements.lock", temp / "requirements.lock")
        shutil.copyfile(materials_dir / "tectonic", temp / "tectonic")
        shutil.copytree(materials_dir / "wheels", temp / "wheels")
        (temp / "metadata").mkdir()
        shutil.copyfile(src_dir / "metadata" / "source_manifest.json", temp / "metadata" / "source_manifest.json")
        shutil.copyfile(materials_dir / "materials-manifest.json", temp / "metadata" / "materials-manifest.json")
        (temp / "metadata" / "static_verification.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        # Metadata is excluded from the build COPY; no secret or original PDF may enter stage.
        os.rename(temp, out)
        return result
    except BaseException:
        shutil.rmtree(temp, ignore_errors=True)
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-context", required=True, type=Path)
    parser.add_argument("--materials", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    a = parser.parse_args()
    try:
        r = assemble(a.source_context, a.materials, a.out)
    except (OSError, ValueError, KeyError, TypeError, PreflightError) as exc:
        parser.exit(2, f"MATERIALS_VERIFICATION_FAILED: {exc}\n")
    print(f"BUILD_CONTEXT_PREPARED commit={r['subject_commit_sha']} wheels={r['wheel_count']} state={r['state']}")
    print("NOT AN IMAGE BUILD, CONTAINER VALIDATION, OR E2E RESULT")


if __name__ == "__main__":
    main()
