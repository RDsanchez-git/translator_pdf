#!/usr/bin/env python3
"""I0-1B inert resolution-INPUT planner; never invokes uv, pip, Docker, or network.

Plans are NOT approved acquisition instructions; exact resolver CLI, version and
binary identity need external confirmation. Requires an externally trusted I0-1
manifest SHA-256 and verifies the entire frozen snapshot before emitting inputs.
"""
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import tempfile
import tomllib

from packaging.requirements import Requirement
from verify_materials import (PreflightError, SUBJECT_COMMIT, SUBJECT_TREE,
                              SUBJECT_DIRECT_REQUIREMENTS, SHA_RE,
                              verify_source_snapshot)

UV_PROPOSED_VERSION = '0.12.20'  # Candidate only; no binary/digest approved
GROQ_CONSTRAINT = 'groq==1.4.0'  # Instrumental constraint; not historical


class PlanError(Exception):
    pass


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def generate(source: Path, out: Path, *, expected_source_manifest_sha256: str,
             python_patch: str | None = None, cutoff_utc: str | None = None) -> dict:
    """Prepare inert inputs from a COMPLETE, externally SHA-anchored I0-1 snapshot."""
    source, out = source.absolute(), out.absolute()
    if not source.is_dir() or out.exists() or not out.parent.is_dir():
        raise PlanError('Snapshot missing or output is not a new directory')
    if (source == out or source in out.parents or out in source.parents
            or source.is_symlink() or out.parent.is_symlink()):
        raise PlanError('Output and source must be disjoint non-symlink trees')
    if not isinstance(expected_source_manifest_sha256, str) or not SHA_RE.fullmatch(expected_source_manifest_sha256):
        raise PlanError('An externally recorded I0-1 SHA-256 is mandatory')
    if python_patch is not None and not re.fullmatch(r'3\.11\.(0|[1-9][0-9]*)', python_patch):
        raise PlanError('Python target must be a specific CPython 3.11.x patch')
    if cutoff_utc is not None:
        try:
            if (not re.fullmatch(r'20\d\d-\d\d-\d\dT\d\d:\d\d:\d\dZ', cutoff_utc)
                    or datetime.strptime(cutoff_utc, '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%dT%H:%M:%SZ') != cutoff_utc):
                raise ValueError('Invalid UTC timestamp')
        except ValueError as exc:
            raise PlanError('Cutoff must be a valid UTC RFC3339 timestamp') from exc
    try:
        snapshot = verify_source_snapshot(source)
    except (PreflightError, ValueError, KeyError, TypeError) as exc:
        raise PlanError(f'Full I0-1 snapshot verification failed: {exc}') from exc
    if (snapshot['source_manifest_sha256'] != expected_source_manifest_sha256
            or snapshot['subject_commit_sha'] != SUBJECT_COMMIT
            or snapshot['subject_tree_sha'] != SUBJECT_TREE):
        raise PlanError('Snapshot identity differs from externally approved subject/manifest SHA')
    project_path = source / 'src' / 'pyproject.toml'
    raw_pyproject = project_path.read_bytes()
    project = tomllib.loads(raw_pyproject.decode('utf-8', 'strict'))
    dependencies = project.get('project', {}).get('dependencies')
    if (not isinstance(dependencies, list) or len(dependencies) != SUBJECT_DIRECT_REQUIREMENTS
            or not all(isinstance(x, str) and x and '\n' not in x and '\r' not in x for x in dependencies)):
        raise PlanError('Snapshot direct runtime requirements differ from frozen subject')
    for item in dependencies:
        try:
            req = Requirement(item)
        except ValueError as exc:
            raise PlanError('Invalid project PEP-508 requirement') from exc
        if req.url is not None:
            raise PlanError('URL/VCS/local dependency requires separate review')
    groq = [Requirement(x) for x in dependencies if Requirement(x).name.lower() == 'groq']
    if len(groq) != 1 or groq[0].specifier or groq[0].extras or groq[0].marker:
        raise PlanError('The characterized direct unpinned Groq requirement differs')
    req_in = ('# Derived from the complete anchored source snapshot (runtime only)\n'
              + '\n'.join(dependencies) + '\n').encode('utf-8')
    constraint = (GROQ_CONSTRAINT + '\n').encode('ascii')
    # Suggested command only; approval of uv binary, exact supported flags,
    # index/cutoff, base image/ABI, and acquisition remains an external gate.
    argv = ['uv', '--no-config', 'pip', 'compile', 'requirements.in',
            '--constraint', 'groq-constraint.in',
            '--python-platform', 'x86_64-unknown-linux-gnu',
            '--python-version', python_patch or '<APPROVED_3.11.PATCH>',
            '--generate-hashes', '--only-binary', ':all:', '--no-python-downloads',
            '--exclude-newer', cutoff_utc or '<APPROVED_UTC_CUTOFF>',
            '--output-file', 'requirements.lock']
    result = {
        'schema_version': 'i0-1b-plan-v2',
        'status': 'INCOMPLETE_NOT_AUTHORIZED_NOT_EXECUTED',
        'subject_commit_sha': snapshot['subject_commit_sha'],
        'subject_tree_sha': snapshot['subject_tree_sha'],
        'source_manifest_sha256': expected_source_manifest_sha256,
        'pyproject_sha256': sha256(raw_pyproject),
        'requirements_in_sha256': sha256(req_in),
        'constraint_sha256': sha256(constraint),
        'runtime_direct_count': len(dependencies),
        'groq_pin_kind': 'INSTRUMENTAL_NOT_HISTORICAL',
        'resolver': {'name': 'uv', 'proposed_version': UV_PROPOSED_VERSION,
                     'binary_sha256': None, 'origin': None, 'approved': False},
        'target': {'os': 'linux', 'arch': 'amd64', 'implementation': 'CPython',
                   'python_version': python_patch, 'libc': None, 'base_image_digest': None},
        'registry_cutoff_utc': cutoff_utc, 'index_identity': None,
        'future_command_argv_NOT_APPROVED_OR_VALIDATED': argv,
        'performed_actions': ['local_read_only_source_validation', 'local_write_inert_plan'],
        'performed_resolution': False,
        'performed_download': False,
        'prohibitions': ['no product edits', 'no Windows pip freeze', 'no sdist',
                         'no resolver execution without separate approval',
                         'no Docker/installer/E2E invocation'],
    }
    tmp = Path(tempfile.mkdtemp(prefix='.i0-1b-plan-incomplete-', dir=out.parent))
    try:
        (tmp / 'requirements.in').write_bytes(req_in)
        (tmp / 'groq-constraint.in').write_bytes(constraint)
        (tmp / 'resolution-plan.json').write_text(
            json.dumps(result, sort_keys=True, indent=2) + '\n', encoding='utf-8')
        os.rename(tmp, out)
        return result
    except BaseException:
        shutil.rmtree(tmp, ignore_errors=True)
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-context', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--expected-source-manifest-sha256', required=True)
    parser.add_argument('--python-patch')
    parser.add_argument('--cutoff-utc')
    args = parser.parse_args()
    try:
        result = generate(args.source_context, args.out,
                          expected_source_manifest_sha256=args.expected_source_manifest_sha256,
                          python_patch=args.python_patch, cutoff_utc=args.cutoff_utc)
    except (OSError, ValueError, KeyError, TypeError, PlanError) as exc:
        parser.exit(2, f'HARNESS_FAILURE: {exc}\n')
    print(f"I0-1B INPUT PLAN ONLY: {result['status']}; uv/pip/network/Docker/product NOT RUN")


if __name__ == '__main__':
    main()
