"""Offline-only tests using synthetic repositories and fake bytes (NEVER run the product)."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

BUILD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BUILD))
from prepare_source import PreflightError, make_source
from verify_materials import assemble, digest, parse_lock, verify


def command(root: Path, *args: str) -> str:
    cp = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=True)
    return cp.stdout.strip()


class BuildInputsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.work = Path(self.tmp.name)
        self.repo = self.work / "repo"
        self.repo.mkdir()
        command(self.repo, "init", "-q")
        command(self.repo, "config", "user.email", "audit-test@example.invalid")
        command(self.repo, "config", "user.name", "Audit Fixture")
        sources = {
            "pyproject.toml": '[project]\nname = "fixture"\nversion = "0.1.0"\ndependencies = ["groq"]\n',
            "apps/main.py": 'SENTINEL = "committed"\n',
            "infra/db/schema_queue.sql": 'CREATE TABLE t (id TEXT);\n',
            ".env": "TOP_SECRET_SHOULD_NOT_COPY=SHHH\n",
            "tests/corpus/canonical/pdf/doc_01.pdf": "FAKE PRIVATE PDF\n",
            "data/myprivate.db": "DO NOT COPY\n",
            "apps/private.key": "SENSITIVE KEY\n",
            "infra/benchmarks/results/run1/raw_vectors.json": '{"sensitive": true}\n',
        }
        for name, data in sources.items():
            p = self.repo / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(data, encoding="utf-8")
        command(self.repo, "add", "-A")
        command(self.repo, "commit", "-qm", "synthetic fixture")
        self.commit = command(self.repo, "rev-parse", "HEAD")
        # Working tree changed: source must still come from commit.
        (self.repo / "apps/main.py").write_text('SENTINEL = "uncommitted"\n')
        self.source = self.work / "source"

    def source_context(self):
        return make_source(self.repo, self.commit, self.source, BUILD / "source_policy.json")

    def materials(self):
        m = self.work / "materials"
        (m / "wheels").mkdir(parents=True)
        wheel = b"SYNTHETIC_TEST_ONLY_NOT_A_VALID_WHEEL"
        (m / "wheels" / "groq-1.4.0-py3-none-any.whl").write_bytes(wheel)
        lock = f"groq==1.4.0 --hash=sha256:{digest(wheel)}\n".encode()
        (m / "requirements.lock").write_bytes(lock)
        (m / "tectonic").write_bytes(b"FAKE_TECTONIC_FOR_TEST")
        manifest = {"schema_version": "1.0", "status": "APPROVED_MATERIALS",
                    "target_platform": "linux/amd64", "python_version": "3.11",
                    "groq_version": "1.4.0", "base_image": "python:3.11-slim@sha256:" + "a" * 64,
                    "files": {"requirements.lock": digest(lock),
                              "tectonic": digest(b"FAKE_TECTONIC_FOR_TEST"),
                              "wheels/groq-1.4.0-py3-none-any.whl": digest(wheel)}}
        (m / "materials-manifest.json").write_text(json.dumps(manifest))
        return m

    def test_source_snapshot_committed_only_and_positive_list(self):
        p = self.source_context()
        names = {a["path"] for a in p["included_files"]}
        self.assertEqual(names, {"apps/main.py", "infra/db/schema_queue.sql", "pyproject.toml"})
        self.assertIn("committed", (self.source / "src/apps/main.py").read_text())
        self.assertNotIn("uncommitted", (self.source / "src/apps/main.py").read_text())
        self.assertFalse((self.source / "src/.env").exists())
        self.assertFalse((self.source / "src/tests").exists())
        self.assertFalse((self.source / "src/data").exists())
        self.assertEqual(p["subject_commit_sha"], self.commit)
        self.assertTrue((self.source / "Dockerfile.audit").is_file())
        self.assertTrue((self.source / ".dockerignore").is_file())

    def test_refuse_output_inside_repo(self):
        with self.assertRaises(PreflightError):
            make_source(self.repo, self.commit, self.repo / "bad", BUILD / "source_policy.json")

    def test_static_verification_and_assembly(self):
        self.source_context()
        m = self.materials()
        p = verify(self.source, m)
        self.assertEqual(p["state"], "STATIC_MATERIALS_VERIFIED_NOT_BUILT")
        context = self.work / "assembled"
        assemble(self.source, m, context)
        self.assertTrue((context / "src/apps/main.py").exists())
        self.assertTrue((context / "metadata/static_verification.json").exists())

    def test_materials_unexpected_secret_rejected(self):
        self.source_context()
        m = self.materials()
        (m / ".env").write_text("SENSITIVE")
        with self.assertRaises(PreflightError):
            verify(self.source, m)

    def test_corrupted_wheel_rejected(self):
        self.source_context()
        m = self.materials()
        (m / "wheels/groq-1.4.0-py3-none-any.whl").write_bytes(b"corrupt")
        with self.assertRaises(PreflightError):
            verify(self.source, m)

    def test_missing_digest_rejected(self):
        self.source_context()
        m = self.materials()
        meta = m / "materials-manifest.json"
        a = json.loads(meta.read_text())
        a["files"]["tectonic"] = None
        meta.write_text(json.dumps(a))
        with self.assertRaises(PreflightError):
            verify(self.source, m)

    def test_tampered_snapshot_dockerignore_rejected(self):
        self.source_context()
        m = self.materials()
        (self.source / ".dockerignore").write_text("**\n!**\n")
        with self.assertRaises(PreflightError):
            verify(self.source, m)

    def test_tampered_snapshot_dockerfile_rejected(self):
        self.source_context()
        m = self.materials()
        (self.source / "Dockerfile.audit").write_text("FROM untrusted-image\n")
        with self.assertRaises(PreflightError):
            verify(self.source, m)

    def test_hard_denies_even_with_relaxed_policy(self):
        from prepare_source import allowed
        policy = json.loads((BUILD / "source_policy.json").read_text())
        policy["allowed_roots"]["tests"] = [".pdf"]
        policy["allowed_exact_files"].append(".env")
        self.assertFalse(allowed("tests/corpus/doc.pdf", policy))
        self.assertFalse(allowed(".env", policy))

    def test_lock_rejects_url_and_unhashed(self):
        for txt in (b"groq==1.4.0\n", b"-e https://evil.invalid/sdk\n", b"groq @ https://evil.invalid/sdk\n"):
            with self.subTest(txt=txt):
                with self.assertRaises(PreflightError):
                    parse_lock(txt)

    def test_template_cannot_pass_verification(self):
        self.source_context()
        m = self.materials()
        template = BUILD / "materials-manifest.template.json"
        (m / "materials-manifest.json").write_bytes(template.read_bytes())
        with self.assertRaises(PreflightError):
            verify(self.source, m)


if __name__ == "__main__":
    unittest.main()
