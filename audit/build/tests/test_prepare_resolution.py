"""I0-1B planner regressions: synthetic Git snapshots, no resolver/network/install."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import prepare_resolution as planner
import verify_materials as verifier
from prepare_source import make_source

BUILD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BUILD))




def git(path: Path, *args: str) -> str:
    return subprocess.run(['git', '-C', str(path), *args], check=True,
                          capture_output=True, text=True).stdout.strip()


class ResolutionInputTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.repo = self.root / 'repo'
        self.repo.mkdir()
        git(self.repo, 'init', '-q')
        git(self.repo, 'config', 'user.email', 'fixture@example.invalid')
        git(self.repo, 'config', 'user.name', 'Synthetic Fixture')
        self.deps = ['groq'] + [f'pkg{i}>=1' for i in range(23)]
        self.snapshot = self.root / 'snapshot'

    def prepare(self, deps=None):
        actual = deps if deps is not None else self.deps
        pyproject = '[project]\nname="fixture"\nversion="0.1.0"\ndependencies=' + json.dumps(actual) + '\n'
        (self.repo / 'pyproject.toml').write_text(pyproject, encoding='utf-8')
        (self.repo / 'apps').mkdir(exist_ok=True)
        (self.repo / 'apps' / 'main.py').write_text('SENTINEL="committed"\n')
        git(self.repo, 'add', '-A')
        git(self.repo, 'commit', '-qm', 'fixture subject')
        sha = git(self.repo, 'rev-parse', 'HEAD')
        tree = git(self.repo, 'rev-parse', 'HEAD^{tree}')
        manifest = make_source(self.repo, sha, self.snapshot, BUILD / 'source_policy.json')
        expected = hashlib.sha256((self.snapshot / 'metadata' / 'source_manifest.json').read_bytes()).hexdigest()
        return sha, tree, manifest, expected

    def execute(self, sha, tree, expected, **kwargs):
        with (mock.patch.object(verifier, 'SUBJECT_COMMIT', sha),
              mock.patch.object(verifier, 'SUBJECT_TREE', tree),
              mock.patch.object(verifier, 'SUBJECT_FILES', 2),
              mock.patch.object(planner, 'SUBJECT_COMMIT', sha),
              mock.patch.object(planner, 'SUBJECT_TREE', tree)):
            return planner.generate(self.snapshot, self.root / 'plan',
                                    expected_source_manifest_sha256=expected, **kwargs)

    def assert_plan_rejected(self, fragment, sha, tree, expected, **kwargs):
        with self.assertRaises(planner.PlanError) as caught:
            self.execute(sha, tree, expected, **kwargs)
        self.assertIn(fragment.lower(), str(caught.exception).lower())

    def test_plan_validates_full_snapshot_and_is_inert(self):
        sha, tree, _, expected = self.prepare()
        with mock.patch.object(subprocess, 'run', side_effect=AssertionError('planner invoked subprocess')):
            plan = self.execute(sha, tree, expected)
        self.assertEqual(plan['status'], 'INCOMPLETE_NOT_AUTHORIZED_NOT_EXECUTED')
        self.assertFalse(plan['performed_resolution'])
        self.assertFalse(plan['performed_download'])
        self.assertIsNone(plan['resolver']['binary_sha256'])
        self.assertEqual(set(x.name for x in (self.root / 'plan').iterdir()),
                         {'requirements.in', 'groq-constraint.in', 'resolution-plan.json'})
        self.assertEqual((self.root / 'plan' / 'groq-constraint.in').read_text(), 'groq==1.4.0\n')
        self.assertEqual(len((self.root / 'plan' / 'requirements.in').read_text().splitlines()), 25)
        self.assertEqual(plan['source_manifest_sha256'], expected)

    def test_explicit_parameters_never_imply_approval(self):
        sha, tree, _, expected = self.prepare()
        plan = self.execute(sha, tree, expected, python_patch='3.11.9',
                            cutoff_utc='2026-10-15T23:59:59Z')
        self.assertEqual(plan['status'], 'INCOMPLETE_NOT_AUTHORIZED_NOT_EXECUTED')
        self.assertEqual(plan['target']['python_version'], '3.11.9')
        self.assertFalse(plan['resolver']['approved'])
        self.assertIsNone(plan['target']['libc'])

    def test_invalid_anchor_is_rejected(self):
        sha, tree, _, expected = self.prepare()
        self.assert_plan_rejected('external', sha, tree, '0' * 64)
        self.assert_plan_rejected('mandatory', sha, tree, 'broken-sha')

    def test_source_tampering_is_rejected(self):
        sha, tree, _, expected = self.prepare()
        (self.snapshot / 'src' / 'apps' / 'main.py').write_text('ALTERED')
        self.assert_plan_rejected('source file altered', sha, tree, expected)

    def test_provenance_manifest_tampering_is_rejected(self):
        sha, tree, _, expected = self.prepare()
        path = self.snapshot / 'metadata/source_manifest.json'
        obj = json.loads(path.read_text())
        obj['included_count'] = 3
        path.write_text(json.dumps(obj))
        self.assert_plan_rejected('snapshot', sha, tree, expected)

    def test_invalid_cutoff_is_rejected(self):
        sha, tree, _, expected = self.prepare()
        self.assert_plan_rejected('cutoff', sha, tree, expected, cutoff_utc='2026-02-30T00:00:00Z')
        self.assert_plan_rejected('cutoff', sha, tree, expected, cutoff_utc='2026-10-01T10:00:00+00:00')

    def test_python_patch_must_be_311(self):
        sha, tree, _, expected = self.prepare()
        self.assert_plan_rejected('Python target', sha, tree, expected, python_patch='3.12.0')

    def test_direct_url_is_rejected(self):
        sha, tree, _, expected = self.prepare(['groq'] + [
            'pkg0 @ https://example.invalid/pkg0.whl'] + [f'pkg{i}' for i in range(1, 23)])
        self.assert_plan_rejected('URL', sha, tree, expected)

    def test_product_groq_pin_drift_is_rejected(self):
        sha, tree, _, expected = self.prepare(['groq==1.4.0'] + [f'pkg{i}' for i in range(23)])
        self.assert_plan_rejected('Groq', sha, tree, expected)

    def test_untracked_worktree_change_not_in_plan(self):
        sha, tree, _, expected = self.prepare()
        (self.repo / 'pyproject.toml').write_text('[project]\ndependencies=[]\n')
        plan = self.execute(sha, tree, expected)
        self.assertEqual(plan['runtime_direct_count'], 24)
        self.assertIn('groq\n', (self.root / 'plan' / 'requirements.in').read_text())

    def test_new_output_directory_required(self):
        sha, tree, _, expected = self.prepare()
        (self.root / 'plan').mkdir()
        self.assert_plan_rejected('not a new', sha, tree, expected)


if __name__ == '__main__':
    unittest.main()
