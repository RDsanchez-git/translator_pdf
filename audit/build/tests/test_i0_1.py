"""Offline I0-1 regression + I0-1B synthetic gate tests. NO product execution."""
from __future__ import annotations

import base64
import csv
import hashlib
import io
import json
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
import zipfile
from unittest import mock


BUILD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BUILD))

import verify_materials as vm
from prepare_source import PreflightError, allowed, make_source


def command(root: Path, *args: str) -> str:
    return subprocess.run(['git', '-C', str(root), *args], check=True,
                          capture_output=True, text=True).stdout.strip()


def b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(hashlib.sha256(data).digest()).decode().rstrip('=')


def wheel_bytes(name='groq', version='1.4.0', tag='py3-none-any', requires=(),
                omit_record=(), record_without_hash=(), record_without_size=(), corrupt_hash=(),
                extra_files=None, compress=zipfile.ZIP_STORED, duplicate=False,
                meta_add='', metadata_version='2.3') -> tuple[str, bytes]:
    prefix = f'{name.replace("-", "_")}-{version}.dist-info'
    meta = (f'Metadata-Version: {metadata_version}\nName: {name}\nVersion: {version}\n'
            'Requires-Python: >=3.11\n' + ''.join(f'Requires-Dist: {r}\n' for r in requires)
            + meta_add).encode()
    wheel = (f'Wheel-Version: 1.0\nGenerator: synthetic-fixture\nRoot-Is-Purelib: true\n'
             f'Tag: {tag}\n').encode()
    objects = {f'{name}/__init__.py': b'# harmless synthetic package\n',
               f'{prefix}/METADATA': meta, f'{prefix}/WHEEL': wheel}
    objects.update(extra_files or {})
    record_name = f'{prefix}/RECORD'
    buf = io.StringIO(newline='')
    writer = csv.writer(buf, lineterminator='\n')
    for path, data in objects.items():
        if path not in omit_record:
            writer.writerow([path, '' if path in record_without_hash else 'sha256=' +
                             ('A' * 43 if path in corrupt_hash else b64(data)),
                             '' if path in record_without_size else str(len(data))])
    writer.writerow([record_name, '', ''])
    result = io.BytesIO()
    with zipfile.ZipFile(result, 'w', compression=compress) as zip_file:
        for path, data in objects.items():
            zip_file.writestr(path, data)
        if duplicate:
            # Bypass normal warning: deliberate adversarial duplicate name.
            with __import__('warnings').catch_warnings():
                __import__('warnings').simplefilter('ignore', UserWarning)
                zip_file.writestr(f'{name}/__init__.py', b'another')
        zip_file.writestr(record_name, buf.getvalue())
    return f'{name}-{version}-{tag}.whl', result.getvalue()


class BuildInputsTest(unittest.TestCase):
    def setUp(self) -> None:
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.work = Path(t.name)
        self.repo = self.work / 'repo'
        self.repo.mkdir()
        command(self.repo, 'init', '-q')
        command(self.repo, 'config', 'user.email', 'audit-test@example.invalid')
        command(self.repo, 'config', 'user.name', 'Audit Fixture')
        sources = {
            'pyproject.toml': '[project]\nname="fixture"\nversion="0.1.0"\ndependencies=["groq"]\n',
            'apps/main.py': 'SENTINEL="committed"\n',
            'infra/db/schema_queue.sql': 'CREATE TABLE t (id TEXT);\n',
            '.env': 'PRIVATE=SECRET\n',
            'tests/corpus/canonical/pdf/doc_01.pdf': 'FAKE PRIVATE PDF\n',
            'data/myprivate.db': 'DO NOT COPY\n',
            'apps/private.key': 'SENSITIVE KEY\n',
            'infra/benchmarks/results/run1/raw_vectors.json': '{"sensitive":true}\n',
        }
        for name, text in sources.items():
            path = self.repo / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
        command(self.repo, 'add', '-A')
        command(self.repo, 'commit', '-qm', 'synthetic source fixture')
        self.commit = command(self.repo, 'rev-parse', 'HEAD')
        (self.repo / 'apps/main.py').write_text('SENTINEL="uncommitted"\n')
        self.source = self.work / 'source'

    def source_context(self) -> dict:
        return make_source(self.repo, self.commit, self.source, BUILD / 'source_policy.json')

    def materials(self, wheel_specs=None) -> Path:
        m = self.work / 'materials'
        (m / 'wheels').mkdir(parents=True, exist_ok=True)
        packages = wheel_specs if wheel_specs is not None else [wheel_bytes()]
        lock = []
        hashes = {'tectonic': vm.digest(b'FAKE_TECTONIC_FOR_TEST')}
        (m / 'tectonic').write_bytes(b'FAKE_TECTONIC_FOR_TEST')
        for filename, content in packages:
            (m / 'wheels' / filename).write_bytes(content)
            name, version, _, _ = __import__('packaging.utils', fromlist=['parse_wheel_filename']).parse_wheel_filename(filename)
            lock.append(f'{name}=={version} --hash=sha256:{vm.digest(content)}')
            hashes['wheels/' + filename] = vm.digest(content)
        raw_lock = ('\n'.join(lock) + '\n').encode()
        (m / 'requirements.lock').write_bytes(raw_lock)
        hashes['requirements.lock'] = vm.digest(raw_lock)
        manifest = {
            'schema_version': '1.1', 'status': 'APPROVED_MATERIALS',
            'target_platform': 'linux/amd64', 'python_version': '3.11',
            'groq_version': '1.4.0', 'base_image': 'python:3.11-slim@sha256:' + 'a' * 64,
            'target_runtime': {'python_full_version': '3.11.9', 'libc_family': 'glibc',
                               'libc_version': '2.36', 'arch': 'x86_64'},
            'provenance': {'approved_by': 'SYNTHETIC_TEST_ONLY', 'approved_at_utc': '2026-10-16T00:00:00Z',
                           'acquisition_ref': 'SYNTHETIC', 'index_url': 'https://example.invalid/simple',
                           'cutoff_utc': '2026-10-16T00:00:00Z',
                           'resolver': {'name': 'uv', 'version': 'SYNTHETIC', 'binary_sha256': 'b' * 64}},
            'files': hashes,
        }
        (m / 'materials-manifest.json').write_text(json.dumps(manifest, sort_keys=True))
        return m

    def _modify_manifest(self, m, fn):
        p = m / 'materials-manifest.json'
        d = json.loads(p.read_text())
        fn(d)
        p.write_text(json.dumps(d))

    def _replace_wheel(self, m, replacement):
        filename, data = replacement
        p = m / 'wheels' / filename
        p.write_bytes(data)
        digest = vm.digest(data)
        lock = f'groq==1.4.0 --hash=sha256:{digest}\n'.encode()
        (m / 'requirements.lock').write_bytes(lock)
        self._modify_manifest(m, lambda x: x['files'].update({f'wheels/{filename}': digest,
                                                               'requirements.lock': vm.digest(lock)}))

    def assertRejected(self, message_fragment: str, fn):
        with self.assertRaises(PreflightError) as raised:
            fn()
        self.assertIn(message_fragment.lower(), str(raised.exception).lower())

    # Original eleven I0-1 regression expectations, updated for VALID synthetic ZIPs.
    def test_source_snapshot_committed_only_and_positive_list(self):
        source = self.source_context()
        names = {a['path'] for a in source['included_files']}
        self.assertEqual(names, {'apps/main.py', 'infra/db/schema_queue.sql', 'pyproject.toml'})
        self.assertIn('committed', (self.source / 'src/apps/main.py').read_text())
        self.assertNotIn('uncommitted', (self.source / 'src/apps/main.py').read_text())
        self.assertFalse((self.source / 'src/.env').exists())
        self.assertFalse((self.source / 'src/tests').exists())
        self.assertFalse((self.source / 'src/data').exists())
        self.assertEqual(source['subject_commit_sha'], self.commit)
        self.assertTrue((self.source / 'Dockerfile.audit').is_file())
        self.assertTrue((self.source / '.dockerignore').is_file())

    def test_refuse_output_inside_repo(self):
        self.assertRejected('separate', lambda: make_source(
            self.repo, self.commit, self.repo / 'bad', BUILD / 'source_policy.json'))

    def test_static_verification_and_assembly(self):
        self.source_context()
        m = self.materials()
        report = vm._verify_fixture(self.source, m)
        self.assertEqual(report['state'], 'SYNTHETIC_STATIC_VERIFICATION_NOT_ACCREDITED')
        context = self.work / 'assembled'
        result = vm._assemble_fixture(self.source, m, context)
        self.assertEqual(result['state'], 'SYNTHETIC_CONTEXT_NOT_ACCREDITED')
        self.assertTrue((context / 'src/apps/main.py').exists())
        self.assertTrue((context / 'metadata/static_verification.json').exists())

    def test_materials_unexpected_secret_rejected(self):
        self.source_context()
        m = self.materials()
        (m / '.env').write_text('SENSITIVE')
        self.assertRejected('inventory', lambda: vm._verify_fixture(self.source, m))

    def test_corrupted_wheel_rejected(self):
        self.source_context()
        m = self.materials()
        (m / 'wheels/groq-1.4.0-py3-none-any.whl').write_bytes(b'corrupt')
        self.assertRejected('sha-256', lambda: vm._verify_fixture(self.source, m))

    def test_missing_digest_rejected(self):
        self.source_context()
        m = self.materials()
        self._modify_manifest(m, lambda x: x['files'].update(tectonic=None))
        self.assertRejected('invalid materials', lambda: vm._verify_fixture(self.source, m))

    def test_tampered_snapshot_dockerignore_rejected(self):
        self.source_context()
        m = self.materials()
        (self.source / '.dockerignore').write_text('**\n!**\n')
        self.assertRejected('modified', lambda: vm._verify_fixture(self.source, m))

    def test_tampered_snapshot_dockerfile_rejected(self):
        self.source_context()
        m = self.materials()
        (self.source / 'Dockerfile.audit').write_text('FROM untrusted\n')
        self.assertRejected('modified', lambda: vm._verify_fixture(self.source, m))

    def test_hard_denies_even_with_relaxed_policy(self):
        policy = json.loads((BUILD / 'source_policy.json').read_text())
        policy['allowed_roots']['tests'] = ['.pdf']
        policy['allowed_exact_files'].append('.env')
        self.assertFalse(allowed('tests/corpus/doc.pdf', policy))
        self.assertFalse(allowed('.env', policy))

    def test_lock_rejects_url_and_unhashed(self):
        for text in (b'groq==1.4.0\n', b'-e https://evil.invalid/sdk\n',
                     b'groq @ https://evil.invalid/sdk\n'):
            with self.subTest(text=text):
                self.assertRejected('lock', lambda: vm.parse_lock(text))

    def test_template_cannot_pass_verification(self):
        self.source_context()
        m = self.materials()
        shutil.copyfile(BUILD / 'materials-manifest.template.json', m / 'materials-manifest.json')
        self.assertRejected('schema', lambda: vm._verify_fixture(self.source, m))

    # I0-1B negative tests require an otherwise valid source, lock, wheel, and manifest.
    def test_record_corrupt_hash_rejected(self):
        self.source_context()
        m = self.materials()
        self._replace_wheel(m, wheel_bytes(corrupt_hash={'groq/__init__.py'}))
        self.assertRejected('RECORD hash', lambda: vm._verify_fixture(self.source, m))

    def test_record_missing_file_rejected(self):
        self.source_context()
        m = self.materials()
        self._replace_wheel(m, wheel_bytes(omit_record={'groq/__init__.py'}))
        self.assertRejected('RECORD coverage', lambda: vm._verify_fixture(self.source, m))

    def test_record_empty_hash_rejected(self):
        self.source_context()
        m = self.materials()
        self._replace_wheel(m, wheel_bytes(record_without_hash={'groq/__init__.py'}))
        self.assertRejected('RECORD hash', lambda: vm._verify_fixture(self.source, m))

    def test_duplicate_archive_member_rejected(self):
        self.source_context()
        m = self.materials()
        self._replace_wheel(m, wheel_bytes(duplicate=True))
        self.assertRejected('duplicated ZIP path', lambda: vm._verify_fixture(self.source, m))

    def test_zip_member_limit_rejected(self):
        self.source_context()
        m = self.materials()
        self._replace_wheel(m, wheel_bytes(extra_files={f'groq/{i}.py': b'x' for i in range(10)}))
        with mock.patch.object(vm, 'MAX_WHEEL_MEMBERS', 5):
            self.assertRejected('member-count', lambda: vm._verify_fixture(self.source, m))

    def test_zip_compression_ratio_rejected(self):
        self.source_context()
        m = self.materials()
        self._replace_wheel(m, wheel_bytes(extra_files={'groq/bomb.py': b'Z' * 100_000},
                                           compress=zipfile.ZIP_DEFLATED))
        with mock.patch.object(vm, 'MAX_COMPRESSION_RATIO', 10):
            self.assertRejected('decompression limit', lambda: vm._verify_fixture(self.source, m))

    def test_zip_metadata_limit_rejected(self):
        self.source_context()
        m = self.materials()
        self._replace_wheel(m, wheel_bytes(meta_add='X-Extra: ' + 'x' * 5000 + '\n'))
        with mock.patch.object(vm, 'MAX_METADATA_BYTES', 500):
            self.assertRejected('metadata limit', lambda: vm._verify_fixture(self.source, m))

    def test_windows_tag_rejected_with_valid_hash(self):
        self.source_context()
        m = self.materials([wheel_bytes(tag='cp311-cp311-win_amd64')])
        self.assertRejected('incompatible with target', lambda: vm._verify_fixture(self.source, m))

    def test_transitive_missing_rejected(self):
        self.source_context()
        m = self.materials([wheel_bytes(requires=('auxiliary>=2',))])
        self.assertRejected('auxiliary', lambda: vm._verify_fixture(self.source, m))

    def test_transitive_closure_valid(self):
        self.source_context()
        m = self.materials([wheel_bytes(requires=('auxiliary>=2',)),
                            wheel_bytes(name='auxiliary', version='2.1')])
        report = vm._verify_fixture(self.source, m)
        self.assertEqual(report['reachable_distribution_count'], 2)

    def test_transitive_wrong_version_rejected(self):
        self.source_context()
        m = self.materials([wheel_bytes(requires=('auxiliary>=2',)),
                            wheel_bytes(name='auxiliary', version='1.0')])
        self.assertRejected('auxiliary', lambda: vm._verify_fixture(self.source, m))

    def test_extras_transitive_closure(self):
        requirements = {'starter': ['helper[opt]>=1'], 'helper': ["feature; extra == 'opt'"], 'feature': []}
        pins = {key: (vm.Version('1'), frozenset({'a' * 64})) for key in requirements}
        graph = vm.verify_graph(requirements['starter'], {k: v for k, v in pins.items() if k != 'starter'},
                                {x: y for x, y in requirements.items()}, vm._fixture_target().environment)
        self.assertEqual(graph, {'helper', 'feature'})

    def test_extras_marker_disabled_no_false_dependency(self):
        pins = {'helper': (vm.Version('1'), frozenset({'a' * 64}))}
        graph = vm.verify_graph(['helper'], pins,
                                {'helper': ["nonexistent; extra == 'not-requested'"]},
                                vm._fixture_target().environment)
        self.assertEqual(graph, {'helper'})

    def test_platform_marker_disabled(self):
        pins = {'groq': (vm.Version('1.4.0'), frozenset({'a' * 64}))}
        graph = vm.verify_graph(['groq'], pins,
                                {'groq': ["nonexistent; sys_platform == 'win32'"]},
                                vm._fixture_target().environment)
        self.assertEqual(graph, {'groq'})

    def test_subject_identity_is_not_self_comparison(self):
        self.source_context()
        self.assertRejected('subject commit', lambda: vm.verify_source_snapshot(self.source))

    def test_snapshot_tampering_rejected(self):
        self.source_context()
        (self.source / 'src/apps/main.py').write_text('CHANGED\n')
        self.assertRejected('source file altered', lambda: vm.verify_source_snapshot(self.source, fixture=True))

    def test_snapshot_extra_file_rejected(self):
        self.source_context()
        (self.source / 'src/apps/injected.py').write_text('KEY="secret"\n')
        self.assertRejected('inventory', lambda: vm.verify_source_snapshot(self.source, fixture=True))

    def test_source_symlink_rejected(self):
        self.source_context()
        victim = self.source / 'src/apps/main.py'
        victim.unlink()
        try:
            victim.symlink_to(self.repo / 'apps/main.py')
        except (OSError, NotImplementedError):
            self.skipTest('symlinks cannot be created on this machine')
        self.assertRejected('symlink', lambda: vm.verify_source_snapshot(self.source, fixture=True))

    def test_extra_material_symlink_rejected(self):
        self.source_context()
        m = self.materials()
        try:
            (m / 'wheels' / 'other').symlink_to(m / 'tectonic')
        except (OSError, NotImplementedError):
            self.skipTest('symlink permission unavailable')
        self.assertRejected('symlink', lambda: vm._verify_fixture(self.source, m))

    def test_schema_v1_0_rejected(self):
        self.source_context()
        m = self.materials()
        self._modify_manifest(m, lambda x: x.update(schema_version='1.0'))
        self.assertRejected('schema', lambda: vm._verify_fixture(self.source, m))

    def test_missing_provenance_rejected(self):
        self.source_context()
        m = self.materials()
        self._modify_manifest(m, lambda x: x.pop('provenance'))
        self.assertRejected('provenance', lambda: vm._verify_fixture(self.source, m))

    def test_invalid_base_image_digest_rejected(self):
        self.source_context()
        m = self.materials()
        self._modify_manifest(m, lambda x: x.update(base_image='python:latest'))
        self.assertRejected('image', lambda: vm._verify_fixture(self.source, m))

    def test_host_libc_profile_mismatch_rejected(self):
        self.source_context()
        m = self.materials()
        self._modify_manifest(m, lambda x: x['target_runtime'].update(libc_version='2.17'))
        self.assertRejected('runtime', lambda: vm._verify_fixture(self.source, m))

    def test_context_copied_hash_vs_pinned_not_current_source(self):
        self.source_context()
        m = self.materials()
        result = vm._verify_fixture(self.source, m)
        temp = self.work / 'copy'
        shutil.copytree(self.source, temp)
        for name in ['tectonic', 'requirements.lock']:
            shutil.copyfile(m / name, temp / name)
        shutil.copytree(m / 'wheels', temp / 'wheels')
        shutil.copyfile(m / 'materials-manifest.json', temp / 'metadata/materials-manifest.json')
        # Source AND destination changed in exactly the same way after approval.
        for path in (self.source / 'src/apps/main.py', temp / 'src/apps/main.py'):
            path.write_text('MUTATED_AFTER_APPROVAL\n')
        self.assertRejected('copied context differs', lambda: vm._verify_copied_context(
            temp, self.source, m, result))

    def test_context_manifest_origin_race_cannot_redefine_copied_source_hash(self):
        """Adversarial: origin manifest modified AFTER the verified copy."""
        self.source_context()
        m = self.materials()
        result = vm._verify_fixture(self.source, m)
        temp = self.work / 'copy'
        shutil.copytree(self.source, temp)
        shutil.copyfile(m / 'tectonic', temp / 'tectonic')
        shutil.copyfile(m / 'requirements.lock', temp / 'requirements.lock')
        shutil.copytree(m / 'wheels', temp / 'wheels')
        shutil.copyfile(m / 'materials-manifest.json', temp / 'metadata/materials-manifest.json')
        forged_payload = b'FORGED_AFTER_VERIFICATION\n'
        (temp / 'src/apps/main.py').write_bytes(forged_payload)
        source_manifest_path = self.source / 'metadata/source_manifest.json'
        source_manifest = json.loads(source_manifest_path.read_text())
        for row in source_manifest['included_files']:
            if row['path'] == 'apps/main.py':
                row['sha256'] = vm.digest(forged_payload)
                row['bytes'] = len(forged_payload)
        source_manifest_path.write_text(json.dumps(source_manifest))
        self.assertRejected('Copied context differs', lambda: vm._verify_copied_context(
            temp, self.source, m, result))

    def test_context_manifest_origin_race_cannot_redefine_copied_wheel_hash(self):
        """Adversarial: origin materials manifest forged after copying metadata."""
        self.source_context()
        m = self.materials()
        result = vm._verify_fixture(self.source, m)
        temp = self.work / 'copy'
        shutil.copytree(self.source, temp)
        shutil.copyfile(m / 'tectonic', temp / 'tectonic')
        shutil.copyfile(m / 'requirements.lock', temp / 'requirements.lock')
        shutil.copytree(m / 'wheels', temp / 'wheels')
        shutil.copyfile(m / 'materials-manifest.json', temp / 'metadata/materials-manifest.json')
        wheel_name = 'wheels/groq-1.4.0-py3-none-any.whl'
        (temp / wheel_name).write_bytes(b'FORGED_WHEEL_AFTER_VERIFICATION')
        source_mat_manifest_path = m / 'materials-manifest.json'
        mat_manifest = json.loads(source_mat_manifest_path.read_text())
        mat_manifest['files'][wheel_name] = vm.digest((temp / wheel_name).read_bytes())
        source_mat_manifest_path.write_text(json.dumps(mat_manifest))
        self.assertRejected('Copied context differs', lambda: vm._verify_copied_context(
            temp, self.source, m, result))

    def test_context_missing_copied_file_rejected(self):
        self.source_context()
        m = self.materials()
        result = vm._verify_fixture(self.source, m)
        temp = self.work / 'copy'
        shutil.copytree(self.source, temp)
        shutil.copyfile(m / 'tectonic', temp / 'tectonic')
        shutil.copyfile(m / 'requirements.lock', temp / 'requirements.lock')
        shutil.copytree(m / 'wheels', temp / 'wheels')
        shutil.copyfile(m / 'materials-manifest.json', temp / 'metadata/materials-manifest.json')
        (temp / 'src/apps/main.py').unlink()
        self.assertRejected('inventory', lambda: vm._verify_copied_context(temp, self.source, m, result))

    def test_synthetic_context_readonly_but_not_immutable(self):
        self.source_context()
        m = self.materials()
        out = self.work / 'assembled'
        report = vm._assemble_fixture(self.source, m, out)
        self.assertEqual(report['state'], 'SYNTHETIC_CONTEXT_NOT_ACCREDITED')
        self.assertFalse(report['immutability_guaranteed'])
        self.assertFalse(out.stat().st_mode & stat.S_IWUSR)
        self.assertFalse((out / 'src/apps/main.py').stat().st_mode & stat.S_IWUSR)

    def test_record_optional_size_with_hash_still_verified(self):
        self.source_context()
        m = self.materials([wheel_bytes(record_without_size={'groq/__init__.py'})])
        report = vm._verify_fixture(self.source, m)
        self.assertEqual(report['wheel_count'], 1)

    def test_csv_comma_in_record_filename_accepted(self):
        self.source_context()
        m = self.materials([wheel_bytes(extra_files={'groq/file,with,commas.txt': b'csv-safe'})])
        report = vm._verify_fixture(self.source, m)
        self.assertEqual(report['wheel_count'], 1)

    def test_valid_compressed_wheel_accepted(self):
        self.source_context()
        m = self.materials([wheel_bytes(compress=zipfile.ZIP_DEFLATED)])
        self.assertEqual(vm._verify_fixture(self.source, m)['wheel_count'], 1)

    def test_corrupt_zip_crc_rejected_even_with_correct_outer_sha(self):
        self.source_context()
        m = self.materials()
        filename, original = wheel_bytes()
        self.assertIn(b'harmless', original)
        changed = original.replace(b'harmless', b'CORRUPT!', 1)
        self.assertEqual(len(changed), len(original))
        self._replace_wheel(m, (filename, changed))
        self.assertRejected('corrupt/unreadable', lambda: vm._verify_fixture(self.source, m))

    def test_duplicate_pin_alias_and_unterminated_lock_rejected(self):
        h = b'a' * 64
        self.assertRejected('duplicate', lambda: vm.parse_lock(
            b'groq==1.4.0 --hash=sha256:' + h + b'\nGrOq==1.4.0 --hash=sha256:' + h + b'\n'))
        self.assertRejected('unterminated', lambda: vm.parse_lock(
            b'groq==1.4.0 \\'))

    def test_lock_multiline_hash_comment_accepted(self):
        a, b = 'a' * 64, 'b' * 64
        raw = ('# header\n' + 'groq==1.4.0 ' + chr(92) + '\n' +
               f'    --hash=sha256:{a} ' + chr(92) + '\n' +
               f'    --hash=sha256:{b} # only approved wheels downloaded later\n').encode()
        pins = vm.parse_lock(raw)
        self.assertEqual(pins['groq'][1], frozenset({a, b}))

    def test_external_source_manifest_hash_anchor_rejects_forgery(self):
        self.source_context()
        source_result = vm.verify_source_snapshot(self.source, fixture=True)
        vm._check_manifest_anchor(source_result, source_result['source_manifest_sha256'])
        self.assertRejected('externally trusted', lambda: vm._check_manifest_anchor(
            source_result, '0' * 64))

    def test_provenance_declaration_is_not_authentication(self):
        self.source_context()
        m = self.materials()
        output = vm._verify_fixture(self.source, m)
        self.assertFalse(output['provenance_authenticated'])
        self.assertFalse(output['base_image_runtime_binding_verified'])
        self.assertFalse(output['tooling_lock_verified'])
        self.assertFalse(output['installation_or_elf_verified'])

    def test_public_api_has_no_test_target_override(self):
        import inspect
        self.assertNotIn('strict_target', inspect.signature(vm.verify).parameters)
        self.assertNotIn('strict_target', inspect.signature(vm.assemble).parameters)
        # Verify that calling with strict_target raises TypeError (unexpected keyword argument)
        # We use getattr to bypass static type checking
        with self.assertRaises(TypeError) as cm:
            getattr(vm, 'assemble')(self.source, self.work, self.work / 'output',
                                   expected_source_manifest_sha256='a' * 64, strict_target=False)
        self.assertIn('strict_target', str(cm.exception))

    def test_public_production_gate_rejects_non_target(self):
        if sys.version_info[:2] != (3, 11) or sys.platform != 'linux':
            self.assertRejected('requires Linux', lambda: vm.verify(self.source, self.work,
                expected_source_manifest_sha256='a' * 64))
        else:
            self.skipTest('Running real target; checked with frozen subject negative test instead')


if __name__ == '__main__':
    unittest.main()
