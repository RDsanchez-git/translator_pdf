#!/usr/bin/env python3
"""I0-1/I0-1B unified OFFLINE, fail-closed static audit-materials gate.

No resolver, installer, network, Docker, application execution, or E2E activity.
The CLI only accepts the frozen production subject on Linux/amd64 CPython 3.11.
Synthetic tests use private helpers and cannot produce an accredited result.

Static validation does NOT prove provenance authentication, target image/runtime
identity, binary ELF dependencies, installation success, security, or E2E fitness.
"""
from __future__ import annotations

import argparse
import base64
import binascii
import csv
from datetime import datetime, timezone
import email.policy
from email.parser import BytesParser
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import platform
import re
import shutil
import stat
import sys
import tempfile
import tomllib
from collections import deque
from dataclasses import dataclass
from importlib import metadata as importlib_metadata
import zipfile
import zlib
import lzma

from packaging import tags as package_tags
from packaging.markers import default_environment
from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet
from packaging.utils import canonicalize_name, parse_wheel_filename
from packaging.version import Version

from prepare_source import PreflightError

SUBJECT_COMMIT = 'c56f3e124d76ae9f1506e4b12fbf0faa4881b574'
SUBJECT_TREE = 'eb7d2f6770517b72546055f4b611bac4734a3db3'
SUBJECT_FILES = 328
SUBJECT_DIRECT_REQUIREMENTS = 24
SUBJECT_GROQ = Version('1.4.0')  # instrumentation constraint, NOT historical pin
MATERIAL_SCHEMA = '1.1'  # deliberately rejects legacy unbound materials
CHUNK_SIZE = 1 << 20
MAX_WHEEL_MEMBERS = 10_000       # candidates: calibrate on actual wheels before accreditation
MAX_WHEEL_EXPANDED = 2 << 30
MAX_MEMBER_EXPANDED = 1 << 30
MAX_METADATA_BYTES = 16 << 20  # RECORD may be large; candidate, not an approved limit
MAX_COMPRESSION_RATIO = 200

# I0-1C: narrow audited overrides tied to immutable wheel SHA-256.
SCIPY_WHEEL = 'scipy-1.17.1-cp311-cp311-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl'
SCIPY_WHEEL_SHA256 = '43af8d1f3bea642559019edfe64e9b11192a8978efbd1539d7bc2aaa23d92de4'
SCIPY_OVERRATIO_MEMBERS = frozenset({
    'scipy/stats/tests/data/nist_anova/SmLs03.dat',
    'scipy/stats/tests/data/nist_anova/SmLs06.dat',
    'scipy/stats/tests/data/nist_anova/SmLs09.dat',
})
SCIPY_MAX_COMPRESSION_RATIO = 240
TORCH_WHEEL = 'torch-2.14.1-cp311-cp311-manylinux_2_28_x86_64.whl'
TORCH_WHEEL_SHA256 = '305a61f61f35f128579f299c5bd33d475f6a01c6307336139632e30856c4854d'
TORCH_MAX_WHEEL_MEMBERS = 13_100
MAX_LOCK_BYTES = 8 << 20
MAX_MANIFEST_BYTES = 8 << 20

SHA_RE = re.compile(r'[0-9a-f]{64}\Z')
IMAGE_RE = re.compile(r'[a-zA-Z0-9._:/-]+@sha256:[0-9a-f]{64}\Z')
MATERIAL_RE = re.compile(r'(?:requirements\.lock|tectonic|wheels/[A-Za-z0-9_.+\-]+\.whl)\Z')
LOCK_LINE_RE = re.compile(r'([A-Za-z][A-Za-z0-9_.-]*)==([^\s;\\]+)(.*)\Z')
HASH_TOKEN_RE = re.compile(r'--hash=sha256:([0-9a-f]{64})(?![0-9a-f])')
RECORD_HASH_RE = re.compile(r'[A-Za-z0-9_-]{43}\Z')


@dataclass(frozen=True)
class _Target:
    python_full_version: str
    libc_family: str
    libc_version: str
    tags: frozenset
    environment: dict[str, str]
    fixture_only: bool = False


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def digest_path(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(CHUNK_SIZE), b''):
            h.update(chunk)
    return h.hexdigest()


def _regular(root: Path, relative: str) -> Path:
    """Do not resolve leaf symlinks; reject symlink ancestors including root."""
    root = root.absolute()
    if any(p.is_symlink() for p in (root, *root.parents)) or not root.is_dir():
        raise PreflightError(f'Untrusted root directory: {root}')
    candidate = PurePosixPath(relative)
    if (not relative or candidate.is_absolute() or any(p in ('', '.', '..') for p in relative.split('/'))
            or '\\' in relative or '\x00' in relative):
        raise PreflightError(f'Unsafe relative path: {relative!r}')
    path = root
    for part in candidate.parts:
        path = path / part
        if path.is_symlink():
            raise PreflightError(f'Symlink rejected: {relative}')
    if not path.is_file():
        raise PreflightError(f'Missing regular artifact: {relative}')
    return path


def _read_small(path: Path, cap: int) -> bytes:
    if path.stat().st_size > cap:
        raise PreflightError(f'Oversized metadata/lock file: {path.name}')
    return path.read_bytes()


def _safe_rel(relative: str) -> bool:
    return (isinstance(relative, str) and bool(relative) and not relative.startswith('/')
            and '\\' not in relative and '\x00' not in relative
            and all(p not in ('', '.', '..') for p in relative.split('/')))


def _check_inventory(root: Path, expected: set[str]) -> None:
    if root.is_symlink() or not root.is_dir():
        raise PreflightError('Invalid directory root')
    actual: set[str] = set()
    for entry in root.rglob('*'):
        if entry.is_symlink():
            raise PreflightError('Unexpected symlink in material/snapshot tree')
        if entry.is_file():
            rel = entry.relative_to(root).as_posix()
            if rel in actual:
                raise PreflightError('Duplicate inventory entry')
            actual.add(rel)
        elif not entry.is_dir():
            raise PreflightError('Unsupported filesystem entry')
    if actual != expected:
        raise PreflightError(f'Inventory mismatch: missing={sorted(expected - actual)[:6]} '
                             f'extra={sorted(actual - expected)[:6]}')


def _production_target() -> _Target:
    if (sys.platform != 'linux' or platform.machine().lower() not in ('x86_64', 'amd64')
            or sys.implementation.name != 'cpython' or sys.version_info[:2] != (3, 11)):
        raise PreflightError('Accreditation gate requires Linux/amd64 CPython 3.11')
    libc_family, libc_version = platform.libc_ver()
    if libc_family != 'glibc' or not libc_version:
        raise PreflightError('Linux libc identity unavailable or unsupported')
    env = dict(default_environment())
    # Type assertion: default_environment() returns dict[str, str | None]
    # but for our purposes all values are strings
    typed_env: dict[str, str] = {k: str(v) for k, v in env.items() if v is not None}
    return _Target(platform.python_version(), libc_family, libc_version,
                   frozenset(package_tags.sys_tags()), typed_env)


def _fixture_target() -> _Target:
    """PRIVATE: synthetic, non-accrediting tests only; never accepted by CLI."""
    env: dict[str, str] = {str(k): str(v) for k, v in default_environment().items()}
    env.update(python_version='3.11', python_full_version='3.11.9',
               sys_platform='linux', platform_system='Linux', platform_machine='x86_64',
               os_name='posix', implementation_name='cpython',
               platform_python_implementation='CPython')
    return _Target('3.11.9', 'glibc', '2.36', frozenset({package_tags.Tag('py3', 'none', 'any'),
             package_tags.Tag('cp311', 'cp311', 'manylinux_2_17_x86_64')}), env, fixture_only=True)


def verify_source_snapshot(root: Path, *, fixture: bool = False) -> dict:
    """Preserves I0-1 full 328-file SHA inventory and source policy fingerprints."""
    manifest_path = _regular(root, 'metadata/source_manifest.json')
    manifest = json.loads(_read_small(manifest_path, MAX_MANIFEST_BYTES))
    if not isinstance(manifest, dict) or manifest.get('purpose') != 'I0-1 SOURCE SNAPSHOT ONLY; NO BUILD OR RUN':
        raise PreflightError('Unrecognized source snapshot manifest')
    if not fixture and (manifest.get('subject_commit_sha') != SUBJECT_COMMIT
                        or manifest.get('subject_tree_sha') != SUBJECT_TREE
                        or manifest.get('included_count') != SUBJECT_FILES):
        raise PreflightError('Subject commit/tree/count differs from frozen audit subject')
    if not re.fullmatch(r'[0-9a-f]{40}', manifest.get('subject_commit_sha', '')) or not re.fullmatch(
            r'[0-9a-f]{40}', manifest.get('subject_tree_sha', '')):
        raise PreflightError('Invalid source subject identifiers')
    tool_dir = Path(__file__).parent
    for filename, field in (('source_policy.json', 'source_policy_sha256'),
                            ('Dockerfile.audit', 'dockerfile_sha256'),
                            ('.dockerignore', 'dockerignore_sha256')):
        expected = manifest.get(field)
        if not isinstance(expected, str) or not SHA_RE.fullmatch(expected):
            raise PreflightError(f'Missing source tool fingerprint: {field}')
        if digest_path(_regular(tool_dir, filename)) != expected:
            raise PreflightError(f'Pinned instrument policy changed: {filename}')
        if filename != 'source_policy.json' and digest_path(_regular(root, filename)) != expected:
            raise PreflightError(f'Source build-policy file modified: {filename}')
    entries = manifest.get('included_files')
    if not isinstance(entries, list) or not entries or manifest.get('included_count') != len(entries):
        raise PreflightError('Source manifest inventory/count invalid')
    seen: set[str] = set()
    total = 0
    for entry in entries:
        if not isinstance(entry, dict):
            raise PreflightError('Invalid source manifest row')
        rel, expected, size = entry.get('path'), entry.get('sha256'), entry.get('bytes')
        if not isinstance(rel, str):
            raise PreflightError('Invalid source entry: path must be string')
        if (not _safe_rel(rel) or rel in seen or not isinstance(expected, str)
                or not SHA_RE.fullmatch(expected) or type(size) is not int or size < 0):
            raise PreflightError('Invalid source entry/path/hash/size')
        seen.add(rel)
        source = _regular(root, 'src/' + rel)
        if source.stat().st_size != size or digest_path(source) != expected:
            raise PreflightError(f'Source file altered: {rel}')
        total += size
    if manifest.get('included_total_bytes') != total:
        raise PreflightError('Source total bytes mismatch')
    _check_inventory(root / 'src', seen)
    _check_inventory(root, {('src/' + f) for f in seen} | {
        'metadata/source_manifest.json', 'Dockerfile.audit', '.dockerignore'})
    return {'source_manifest_sha256': digest_path(manifest_path),
            'subject_commit_sha': manifest['subject_commit_sha'],
            'subject_tree_sha': manifest['subject_tree_sha'],
            'source_file_count': len(seen)}


def parse_lock(data: bytes) -> dict[str, tuple[Version, frozenset[str]]]:
    """The one accepted grammar: exact pins and sha256 tokens, optional comments."""
    if len(data) > MAX_LOCK_BYTES:
        raise PreflightError('Lock exceeds maximum size')
    try:
        text = data.decode('utf-8', 'strict')
    except UnicodeError as exc:
        raise PreflightError('Lock is not UTF-8') from exc
    lines: list[str] = []
    pending = ''
    for original in text.splitlines():
        line = original.strip()
        if not line or line.startswith('#'):
            continue
        if ' #' in line:
            line = line.split(' #', 1)[0].rstrip()
        if line.endswith('\\'):
            pending += line[:-1].strip() + ' '
            continue
        lines.append((pending + line).strip())
        pending = ''
    if pending:
        raise PreflightError('Unterminated lock continuation')
    result: dict[str, tuple[Version, frozenset[str]]] = {}
    for line in lines:
        match = LOCK_LINE_RE.fullmatch(line)
        if match is None:
            raise PreflightError('Unsupported lock syntax/source/option')
        raw_name, raw_version, tail = match.groups()
        try:
            pin_version = Version(raw_version)
        except ValueError as exc:
            raise PreflightError('Invalid lock version') from exc
        hashes = HASH_TOKEN_RE.findall(tail)
        if not hashes or HASH_TOKEN_RE.sub('', tail).strip():
            raise PreflightError('Missing SHA-256 or extra lock tokens')
        name = canonicalize_name(raw_name)
        if name in result:
            raise PreflightError('Duplicate/colliding distribution in lock')
        result[name] = (pin_version, frozenset(hashes))
    if not result:
        raise PreflightError('Empty lock')
    return result


def _read_record_hash(encoded: str) -> bytes:
    if not encoded.startswith('sha256=') or not RECORD_HASH_RE.fullmatch(encoded[7:]):
        raise PreflightError('Invalid/unsupported RECORD hash (SHA-256 required)')
    try:
        raw = base64.urlsafe_b64decode(encoded[7:] + '=')
    except (ValueError, binascii.Error) as exc:
        raise PreflightError('Malformed base64 in RECORD hash') from exc
    if (len(raw) != 32 or base64.urlsafe_b64encode(raw).decode('ascii').rstrip('=') != encoded[7:]):
        raise PreflightError('Noncanonical RECORD hash')
    return raw


def _safe_member(name: str) -> bool:
    return (_safe_rel(name.rstrip('/')) and not name.startswith('/')
            and not name.endswith('//') and ':' not in name
            and '\r' not in name and '\n' not in name)


def inspect_wheel(path: Path, filename: str, allowed_tags: frozenset,
                  target_python: str) -> tuple[str, Version, list[str]]:
    """Read wheel ZIP once, validate RECORD cryptographically with bounded streaming."""
    try:
        name, version, _, filename_tags = parse_wheel_filename(filename)
    except ValueError as exc:
        raise PreflightError(f'Invalid wheel filename: {filename}') from exc
    if not filename_tags.intersection(allowed_tags):
        raise PreflightError(f'Wheel incompatible with target tags: {filename}')
    scoped_scipy = filename == SCIPY_WHEEL
    scoped_torch = filename == TORCH_WHEEL
    if scoped_scipy and digest_path(path) != SCIPY_WHEEL_SHA256:
        raise PreflightError('SciPy wheel differs from audited ZIP-limit exception')
    if scoped_torch and digest_path(path) != TORCH_WHEEL_SHA256:
        raise PreflightError('Torch wheel differs from audited ZIP-limit exception')
    if path.stat().st_size > MAX_WHEEL_EXPANDED:
        raise PreflightError('Compressed wheel exceeds configured safety limit')
    try:
        with zipfile.ZipFile(path) as archive:
            infos = archive.infolist()
            member_limit = TORCH_MAX_WHEEL_MEMBERS if scoped_torch else MAX_WHEEL_MEMBERS
            if not infos or len(infos) > member_limit:
                raise PreflightError('Wheel member-count limit violated')
            members: dict[str, zipfile.ZipInfo] = {}
            total = 0
            for info in infos:
                member = info.filename
                if not _safe_member(member) or member in members:
                    raise PreflightError('Unsafe/duplicated ZIP path')
                mode = (info.external_attr >> 16) & 0o170000
                if mode not in (0, stat.S_IFREG, stat.S_IFDIR):
                    raise PreflightError('Wheel has symlink or special file')
                if info.is_dir() and mode not in (0, stat.S_IFDIR):
                    raise PreflightError('ZIP directory conflicts with file mode')
                if not info.is_dir() and mode == stat.S_IFDIR:
                    raise PreflightError('ZIP file marked as directory')
                total += info.file_size
                if (total > MAX_WHEEL_EXPANDED or info.file_size > MAX_MEMBER_EXPANDED
                        or (info.file_size and not info.compress_size)
                        or (info.compress_size and info.file_size >
                            (SCIPY_MAX_COMPRESSION_RATIO
                             if scoped_scipy and member in SCIPY_OVERRATIO_MEMBERS
                             else MAX_COMPRESSION_RATIO) * info.compress_size)):
                    raise PreflightError('Wheel decompression limit violated')
                members[member] = info
            regular = {name for name, info in members.items() if not info.is_dir()}
            metadata = [k for k in regular if re.fullmatch(r'[^/]+\.dist-info/METADATA', k)]
            wheel_meta = [k for k in regular if re.fullmatch(r'[^/]+\.dist-info/WHEEL', k)]
            records = [k for k in regular if re.fullmatch(r'[^/]+\.dist-info/RECORD', k)]
            if len(metadata) != 1 or len(wheel_meta) != 1 or len(records) != 1:
                raise PreflightError('Missing/ambiguous wheel metadata/RECORD')
            prefix = metadata[0].split('/', 1)[0]
            expected_prefix = f'{name.replace("-", "_")}-{version}.dist-info'
            if prefix != expected_prefix or any(not k.startswith(prefix + '/') for k in wheel_meta + records):
                raise PreflightError('Wheel dist-info identity differs from filename')
            for key in metadata + wheel_meta + records:
                if members[key].file_size > MAX_METADATA_BYTES:
                    raise PreflightError('Wheel metadata limit violated')
            meta = BytesParser(policy=email.policy.default).parsebytes(archive.read(metadata[0]))
            wheel_headers = BytesParser(policy=email.policy.default).parsebytes(archive.read(wheel_meta[0]))
            with archive.open(records[0]) as record_file:
                record_text = record_file.read(MAX_METADATA_BYTES + 1)
            if len(record_text) > MAX_METADATA_BYTES:
                raise PreflightError('RECORD size limit violated')
            try:
                entries = list(csv.reader(io.StringIO(record_text.decode('utf-8', 'strict'), newline=''),
                                          strict=True))
            except (UnicodeError, csv.Error) as exc:
                raise PreflightError('Malformed CSV/UTF-8 RECORD') from exc
            included: set[str] = set()
            for row in entries:
                if len(row) != 3:
                    raise PreflightError('RECORD row must have three fields')
                member, hash_value, size_text = row
                if member in included or member not in regular:
                    raise PreflightError(f'RECORD missing/duplicate archive entry: {member}')
                included.add(member)
                if member == records[0]:
                    if hash_value or size_text:
                        raise PreflightError('RECORD itself must not have a hash or size')
                    continue
                expected_digest = _read_record_hash(hash_value)
                if size_text:
                    if not size_text.isascii() or not size_text.isdigit():
                        raise PreflightError('RECORD member size invalid')
                    if int(size_text) != members[member].file_size:
                        raise PreflightError(f'RECORD size mismatch: {member}')
                hashed = hashlib.sha256()
                count = 0
                with archive.open(members[member]) as stream:
                    for chunk in iter(lambda: stream.read(CHUNK_SIZE), b''):
                        count += len(chunk)
                        if count > members[member].file_size or count > MAX_MEMBER_EXPANDED:
                            raise PreflightError('ZIP member grew past configured limit')
                        hashed.update(chunk)
                if count != members[member].file_size or hashed.digest() != expected_digest:
                    raise PreflightError(f'RECORD hash/size mismatch: {member}')
            # Historical detached signatures may be deliberately absent from RECORD.
            # We do not authenticate such signatures; provenance stays unaccredited.
            optional_signatures = {records[0] + '.jws', records[0] + '.p7s'}
            if regular - included - optional_signatures:
                raise PreflightError(f'RECORD coverage incomplete: {sorted(regular - included - optional_signatures)[:3]}')
    except PreflightError:
        raise  # PreflightError derives from RuntimeError: preserve precise gate failure.
    except (zipfile.BadZipFile, EOFError, OSError, UnicodeError, RuntimeError,
            NotImplementedError, zlib.error, lzma.LZMAError) as exc:
        raise PreflightError(f'Corrupt/unreadable wheel archive: {filename}') from exc
    try:
        if (canonicalize_name(meta.get('Name', '')) != name
                or Version(meta.get('Version', '')) != version):
            raise PreflightError('Wheel metadata name/version mismatch')
        if not meta.get('Metadata-Version') or len(meta.get_all('Name', [])) != 1 or len(meta.get_all('Version', [])) != 1:
            raise PreflightError('Missing/duplicate core wheel metadata')
        declared_tags = wheel_headers.get_all('Tag', [])
        if (not wheel_headers.get('Wheel-Version', '').startswith('1.')
                or str(wheel_headers.get('Root-Is-Purelib', '')).casefold() not in ('true', 'false')
                or not declared_tags or set(declared_tags) != {str(x) for x in filename_tags}):
            raise PreflightError('Invalid WHEEL header/tags')
        python_spec = meta.get('Requires-Python')
        if python_spec and target_python not in SpecifierSet(python_spec):
            raise PreflightError('Wheel Requires-Python excludes target')
    except ValueError as exc:
        raise PreflightError('Malformed wheel version/Requires-Python') from exc
    requirements = meta.get_all('Requires-Dist', [])
    if not isinstance(requirements, list):
        raise PreflightError('Malformed Requires-Dist metadata')
    return name, version, requirements


def verify_graph(direct: list[str], pins: dict, metadata_requirements: dict,
                 environment: dict[str, str]) -> set[str]:
    """Validate reachable exact-version closure, including parent extras/markers."""
    work: deque[tuple[Requirement, str]] = deque()
    try:
        for raw in direct:
            work.append((Requirement(raw), ''))
    except ValueError as exc:
        raise PreflightError('Invalid direct PEP-508 requirement') from exc
    visited: set[tuple[str, str]] = set()
    active: set[str] = set()
    while work:
        req, parent_extra = work.popleft()
        if req.url is not None:
            raise PreflightError('Direct or transitive URL dependency forbidden')
        try:
            if req.marker is not None and not req.marker.evaluate(dict(environment, extra=parent_extra)):
                continue
        except (ValueError, KeyError) as exc:
            raise PreflightError('Invalid dependency marker') from exc
        name = canonicalize_name(req.name)
        if name not in pins or pins[name][0] not in req.specifier:
            raise PreflightError(f'Missing/incompatible transitively required package: {name} {req.specifier}')
        if name not in metadata_requirements:
            raise PreflightError(f'Missing wheel metadata: {name}')
        active.add(name)
        for extra in sorted({''} | set(req.extras)):
            state = (name, extra)
            if state in visited:
                continue
            visited.add(state)
            for raw in metadata_requirements[name]:
                try:
                    child = Requirement(raw)
                except ValueError as exc:
                    raise PreflightError(f'Invalid Requires-Dist in {name}') from exc
                work.append((child, extra))
    if active != set(pins):
        raise PreflightError(f'Unused/unreachable packages locked: {sorted(set(pins) - active)}')
    return active


def _verify_materials(src: Path, materials: Path, target: _Target) -> dict:
    manifest_path = _regular(materials, 'materials-manifest.json')
    manifest = json.loads(_read_small(manifest_path, MAX_MANIFEST_BYTES))
    if not isinstance(manifest, dict) or any((manifest.get(key) != expected) for key, expected in (
            ('schema_version', MATERIAL_SCHEMA), ('status', 'APPROVED_MATERIALS'),
            ('target_platform', 'linux/amd64'), ('python_version', '3.11'),
            ('groq_version', '1.4.0'))):
        raise PreflightError('Unsupported/unapproved materials manifest schema/identity')
    image = manifest.get('base_image')
    if not isinstance(image, str) or not IMAGE_RE.fullmatch(image):
        raise PreflightError('Image must be named and pinned by sha256 digest')
    runtime = manifest.get('target_runtime')
    if (not isinstance(runtime, dict) or runtime.get('python_full_version') != target.python_full_version
            or runtime.get('libc_family') != target.libc_family
            or runtime.get('libc_version') != target.libc_version
            or runtime.get('arch') != 'x86_64'):
        raise PreflightError('Host target runtime differs from declared build runtime profile')
    provenance = manifest.get('provenance')
    if not isinstance(provenance, dict) or any(not isinstance(provenance.get(k), str) or not provenance[k].strip()
            for k in ('approved_by', 'approved_at_utc', 'acquisition_ref', 'index_url', 'cutoff_utc')):
        raise PreflightError('Required acquisition/provenance assertions missing')
    try:
        for field in ('approved_at_utc', 'cutoff_utc'):
            value = provenance[field]
            if not value.endswith('Z') or datetime.fromisoformat(value.replace('Z', '+00:00')).utcoffset() != timezone.utc.utcoffset(None):
                raise ValueError('Non-UTC time')
        if not provenance['index_url'].startswith('https://'):
            raise ValueError('Insecure provenance registry URL')
    except (ValueError, TypeError) as exc:
        raise PreflightError('Invalid provenance time/index fields') from exc
    resolver = provenance.get('resolver')
    if (not isinstance(resolver, dict) or not isinstance(resolver.get('name'), str)
            or not isinstance(resolver.get('version'), str)
            or not isinstance(resolver.get('binary_sha256'), str)
            or not SHA_RE.fullmatch(resolver['binary_sha256'])):
        raise PreflightError('Resolver provenance fields missing/malformed')
    file_hashes = manifest.get('files')
    if not isinstance(file_hashes, dict) or not {'requirements.lock', 'tectonic'}.issubset(file_hashes):
        raise PreflightError('Materials file index is incomplete')
    if not any(x.startswith('wheels/') for x in file_hashes):
        raise PreflightError('No wheels in materials file index')
    for rel, hex_digest in file_hashes.items():
        if (not isinstance(rel, str) or not MATERIAL_RE.fullmatch(rel)
                or not isinstance(hex_digest, str) or not SHA_RE.fullmatch(hex_digest)):
            raise PreflightError('Invalid materials path/hash in manifest')
    _check_inventory(materials, set(file_hashes) | {'materials-manifest.json'})
    for rel, wanted in file_hashes.items():
        if digest_path(_regular(materials, rel)) != wanted:
            raise PreflightError(f'Materials SHA-256 mismatch: {rel}')
    lock_bytes = _read_small(_regular(materials, 'requirements.lock'), MAX_LOCK_BYTES)
    pins = parse_lock(lock_bytes)
    if pins.get('groq', (None,))[0] != SUBJECT_GROQ:
        raise PreflightError('Required instrumental Groq 1.4.0 constraint missing')
    project = tomllib.loads(_regular(src, 'src/pyproject.toml').read_text(encoding='utf-8'))
    direct = project.get('project', {}).get('dependencies')
    if not isinstance(direct, list) or not direct or not all(isinstance(x, str) for x in direct):
        raise PreflightError('Invalid source project dependencies')
    if not target.fixture_only and len(direct) != SUBJECT_DIRECT_REQUIREMENTS:
        raise PreflightError('Frozen subject direct dependencies changed')
    seen: set[str] = set()
    wheel_reqs: dict[str, list[str]] = {}
    for rel, expected in sorted(file_hashes.items()):
        if not rel.startswith('wheels/'):
            continue
        pkg_name, ver, requirements = inspect_wheel(_regular(materials, rel), rel[7:],
                                                    target.tags, target.python_full_version)
        if (pkg_name in seen or pkg_name not in pins or pins[pkg_name][0] != ver
                or expected not in pins[pkg_name][1]):
            raise PreflightError(f'Duplicate/unpinned/mismatching wheel: {rel}')
        seen.add(pkg_name)
        wheel_reqs[pkg_name] = requirements
    if seen != set(pins):
        raise PreflightError(f'Wheelhouse not exact one-to-one lock closure: {sorted(set(pins)-seen)}')
    env = dict(target.environment)
    env.update(python_version='3.11', python_full_version=target.python_full_version,
               sys_platform='linux', platform_system='Linux', platform_machine='x86_64',
               os_name='posix', implementation_name='cpython',
               platform_python_implementation='CPython')
    reachable = verify_graph(direct, pins, wheel_reqs, env)
    return {'material_schema': MATERIAL_SCHEMA, 'locked_distribution_count': len(pins),
            'wheel_count': len(seen), 'reachable_distribution_count': len(reachable),
            'lock_sha256': digest(lock_bytes), 'materials_manifest_sha256': digest_path(manifest_path),
            'base_image': image, 'target_runtime': runtime,
            'packaging_tool_version_observed': importlib_metadata.version('packaging'),
            'provenance_fields_present': True, 'provenance_authenticated': False,
            'base_image_runtime_binding_verified': False,
            'installation_or_elf_verified': False,
            'tooling_lock_verified': False,
            'accreditation': 'NOT_ACCREDITED_SYNTHETIC' if target.fixture_only else 'STATIC_ONLY_EXTERNAL_EVIDENCE_PENDING'}


def _check_manifest_anchor(result: dict, trusted_sha256: str) -> None:
    if (not isinstance(trusted_sha256, str) or not SHA_RE.fullmatch(trusted_sha256)
            or result['source_manifest_sha256'] != trusted_sha256):
        raise PreflightError('Frozen source manifest differs from externally trusted I0-1 SHA-256')


def verify(src_dir: Path, materials_dir: Path, *, expected_source_manifest_sha256: str) -> dict:
    """Production-only gate requires I0-1 source manifest SHA as external trust anchor."""
    target = _production_target()
    src = src_dir.absolute()
    materials = materials_dir.absolute()
    source_result = verify_source_snapshot(src)
    _check_manifest_anchor(source_result, expected_source_manifest_sha256)
    return {**source_result, **_verify_materials(src, materials, target),
            'state': 'STATIC_MATERIALS_VERIFIED_NOT_BUILT'}


def _verify_fixture(src: Path, materials: Path) -> dict:
    """Synthetic-unit-test-only. Its results are NOT eligible for build or HV."""
    target = _fixture_target()
    return {**verify_source_snapshot(src, fixture=True), **_verify_materials(src, materials, target),
            'state': 'SYNTHETIC_STATIC_VERIFICATION_NOT_ACCREDITED'}


def _readonly_tree(root: Path) -> None:
    for entry in sorted(root.rglob('*'), key=lambda x: len(x.parts), reverse=True):
        if entry.is_file():
            entry.chmod(0o444)
        elif entry.is_dir():
            entry.chmod(0o555)
    root.chmod(0o555)


def _verify_copied_context(temp: Path, source: Path, materials: Path, result: dict) -> None:
    """Compare copied bytes with ORIGINAL PINNED manifest, not current source files."""
    # The manifest bytes inspected here MUST be the pinned bytes in the copied
    # context. Re-reading mutable source/material manifests would create a race:
    # an attacker could change an original manifest after its copy and redefine
    # the expected digests for subsequently copied payload files.
    copied_src_manifest = _regular(temp, 'metadata/source_manifest.json')
    copied_mat_manifest = _regular(temp, 'metadata/materials-manifest.json')
    if digest_path(copied_src_manifest) != result['source_manifest_sha256']:
        raise PreflightError('Copied source manifest differs from verified original')
    if digest_path(copied_mat_manifest) != result['materials_manifest_sha256']:
        raise PreflightError('Copied materials manifest differs from verified original')
    src_manifest = json.loads(_read_small(copied_src_manifest, MAX_MANIFEST_BYTES))
    mat_manifest = json.loads(_read_small(copied_mat_manifest, MAX_MANIFEST_BYTES))
    expected = {'metadata/source_manifest.json': result['source_manifest_sha256'],
                'metadata/materials-manifest.json': result['materials_manifest_sha256']}
    expected['Dockerfile.audit'] = src_manifest['dockerfile_sha256']
    expected['.dockerignore'] = src_manifest['dockerignore_sha256']
    expected.update({'src/' + row['path']: row['sha256'] for row in src_manifest['included_files']})
    expected.update(mat_manifest['files'])
    _check_inventory(temp, set(expected))
    for rel, sha256 in expected.items():
        if digest_path(_regular(temp, rel)) != sha256:
            raise PreflightError(f'Copied context differs from frozen manifest: {rel}')


def _assemble_core(src_dir: Path, materials_dir: Path, out: Path, target: _Target,
                   trusted_source_manifest_sha256: str | None = None) -> dict:
    src, materials, out = src_dir.absolute(), materials_dir.absolute(), out.absolute()
    for path in (src, materials, out.parent):
        if path.is_symlink():
            raise PreflightError('Symlinked root or output parent not permitted')
    if out.exists() or not out.parent.is_dir():
        raise PreflightError('Output must be a NEW directory below an existing parent')
    if any(out == p or out in p.parents or p in out.parents for p in (src, materials)):
        raise PreflightError('Output, source, materials must be disjoint')
    source_result = verify_source_snapshot(src, fixture=target.fixture_only)
    if not target.fixture_only:
        if trusted_source_manifest_sha256 is None:
            raise PreflightError('Production mode requires trusted source manifest SHA-256')
        _check_manifest_anchor(source_result, trusted_source_manifest_sha256)
    result = {**source_result, **_verify_materials(src, materials, target)}
    temp = Path(tempfile.mkdtemp(prefix='.audit-build-incomplete-', dir=out.parent))
    try:
        shutil.copytree(src / 'src', temp / 'src')
        shutil.copyfile(_regular(src, 'Dockerfile.audit'), temp / 'Dockerfile.audit')
        shutil.copyfile(_regular(src, '.dockerignore'), temp / '.dockerignore')
        shutil.copyfile(_regular(materials, 'requirements.lock'), temp / 'requirements.lock')
        shutil.copyfile(_regular(materials, 'tectonic'), temp / 'tectonic')
        shutil.copytree(materials / 'wheels', temp / 'wheels')
        (temp / 'metadata').mkdir()
        shutil.copyfile(_regular(src, 'metadata/source_manifest.json'), temp / 'metadata/source_manifest.json')
        shutil.copyfile(_regular(materials, 'materials-manifest.json'), temp / 'metadata/materials-manifest.json')
        _verify_copied_context(temp, src, materials, result)
        report = {**result, 'state': ('SYNTHETIC_CONTEXT_NOT_ACCREDITED' if target.fixture_only
                                     else 'STATIC_CONTEXT_COPIED_VERIFIED_NOT_BUILT'),
                  'postcopy_all_manifest_hashes_checked': True,
                  'immutability_guaranteed': False}
        (temp / 'metadata' / 'static_verification.json').write_text(
            json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
        _readonly_tree(temp)
        os.rename(temp, out)
        return report
    except BaseException:
        # chmod may have made the root read-only; restore before cleanup.
        for entry in temp.rglob('*'):
            if entry.is_dir():
                entry.chmod(0o755)
        temp.chmod(0o755)
        shutil.rmtree(temp, ignore_errors=True)
        raise


def assemble(src_dir: Path, materials_dir: Path, out: Path, *,
             expected_source_manifest_sha256: str) -> dict:
    """Strict entry: production host + frozen subject + externally pinned source manifest."""
    return _assemble_core(src_dir, materials_dir, out, _production_target(),
                          expected_source_manifest_sha256)


def _assemble_fixture(src: Path, materials: Path, out: Path) -> dict:
    """Private synthetic-test entry; output explicitly NOT ACCREDITED."""
    return _assemble_core(src, materials, out, _fixture_target())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-context', type=Path, required=True)
    parser.add_argument('--materials', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--expected-source-manifest-sha256', required=True,
                        help='SHA-256 of source_manifest.json measured at the approved I0-1 checkpoint')
    args = parser.parse_args()
    try:
        result = assemble(args.source_context, args.materials, args.out,
                          expected_source_manifest_sha256=args.expected_source_manifest_sha256)
    except (PreflightError, OSError, ValueError, TypeError, KeyError, OverflowError) as exc:
        parser.exit(2, f'HARNESS_FAILURE: {exc}\n')
    print('STATIC_CONTEXT_PREPARED ' + json.dumps(result, sort_keys=True))
    print('NOT PROVENANCE AUTHENTICATION, BUILD, HV, CONTAINER OR E2E RESULT')


if __name__ == '__main__':
    main()
