"""B03.2: Isolated single-container OCR -> G3 fake -> G5 PDF laboratory.

Host launcher and in-container entry point. The working tree is mounted read-only;
state, data, output and caches live in a fresh host temp directory per run.
The container has `--network none`; fake Groq only listens on 127.0.0.1. This
is a pipeline/compilation smoke test, NEVER a translation or scientific PASS.

Do not run historical G4 scripts or copy their databases into this laboratory.
"""
from __future__ import annotations

import argparse
from contextlib import closing
import hashlib
import os
from pathlib import Path, PurePosixPath
import shutil
import sqlite3
import subprocess
import sys
import tarfile
import tempfile
import threading
import uuid
import zipfile

RUNTIME_IMAGE = "i0-1d/translator-pdf-runtime:r2-d4cda2c-20261031_211824"
IMAGE_ID = "sha256:abe5b5dbbc65e8920e0948b189bd9bd090eb395e99420918190128a2ec12b4bd"
HISTORY_ZIP = "PAQUETE_HISTORICO_G4_B03_PDF_A_PDF_FBF166B_R1.zip"
HISTORY_HASH = "ac0300bc0a2a6ac8117f8fb34af000ba91747f2761e5562ba5bb4ae14fccf76d"
G4_TAR_BASENAME = "B03_VOLUMES_Y_SQLITE_BACKUP.tar"
DUMMY_KEY = "translator-pdf-g3-offline-fake-only"
OPT_IN = "EXPLICIT_OFFLINE_TEST_ONLY"


class LabError(RuntimeError):
    pass


def _sha(path: Path) -> str:
    d = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            d.update(chunk)
    return d.hexdigest()


def _check_checkout(root: Path) -> None:
    required = (
        "apps/cli/pdf_product.py", "apps/lab/g3_fake.py",
        "apps/lab/offline_pdf_lab.py", "infra/db/bootstrap.py",
        "apps/compiler/tectonic_runner.py", "runtime/engine.py",
    )
    missing = [s for s in required if not (root / s).is_file()]
    if missing:
        raise LabError("B032_WORKTREE_MISSING: " + ", ".join(missing))
    if (root / "apps/lab/offline_pdf_lab.py").resolve() != Path(__file__).resolve():
        raise LabError("B032_MUST_USE_CURRENT_CHECKOUT")


def _check_history(archive: Path) -> None:
    if not archive.is_file() or archive.is_symlink():
        raise LabError("B032_HISTORY_ZIP_NOT_FOUND: " + str(archive))
    if _sha(archive) != HISTORY_HASH:
        raise LabError("B032_HISTORY_ZIP_HASH_MISMATCH")
    with zipfile.ZipFile(archive) as z:
        matches = [p for p in z.namelist() if p.endswith("/" + G4_TAR_BASENAME)]
        if len(matches) != 1:
            raise LabError("B032_HISTORY_TAR_MISSING_OR_AMBIGUOUS")


def _docker_image_id() -> str:
    try:
        ctx = subprocess.run(["docker", "context", "show"], check=True,
                             capture_output=True, text=True, timeout=20)
        if ctx.stdout.strip() != "desktop-linux":
            raise LabError("B032_DOCKER_CONTEXT_NOT_DESKTOP_LINUX: " + ctx.stdout.strip())
        result = subprocess.run(["docker", "image", "inspect", RUNTIME_IMAGE,
                                 "--format", "{{.Id}}"], check=True,
                                capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        raise LabError("B032_DOCKER_OR_IMAGE_UNAVAILABLE") from exc
    image_id = result.stdout.strip()
    if image_id != IMAGE_ID:
        raise LabError("B032_IMAGE_ID_DRIFT: " + image_id)
    return image_id


def _cache_destination(member: tarfile.TarInfo, workspace: Path) -> Path | None:
    """Allow only two historical cache trees; reject all other tar entries."""
    path = PurePosixPath(member.name)
    parts = path.parts
    if not parts or path.is_absolute() or ".." in parts or "\\" in member.name:
        raise LabError("B032_UNSAFE_ARCHIVE_PATH")
    if len(parts) <= 2 or parts[:2] != ("volumes", "tectonic_cache"):
        if parts[:3] == ("volumes", "g3_runtime_data", "tiktoken-cache") and len(parts) > 3:
            dest = workspace / "data" / "tiktoken-cache"
            return dest.joinpath(*parts[3:])
        return None
    return (workspace / "cache").joinpath(*parts[2:])


def _seed_caches(archive: Path, workspace: Path) -> tuple[int, int]:
    """Stream only pinned G4 caches. Never extract historical DB/AST/PDF/receipts."""
    counts = {"tectonic": 0, "tiktoken": 0}
    bytes_seen = 0
    with zipfile.ZipFile(archive) as z:
        name = next(s for s in z.namelist() if s.endswith("/" + G4_TAR_BASENAME))
        with z.open(name) as stream, tarfile.open(fileobj=stream, mode="r|") as tar:
            for member in tar:
                dst = _cache_destination(member, workspace)
                if dst is None:
                    continue
                if not member.isfile() or member.size > 32 * 1024 * 1024:
                    raise LabError("B032_UNSUPPORTED_CACHE_ARCHIVE_ENTRY")
                bytes_seen += member.size
                if bytes_seen > 80 * 1024 * 1024:
                    raise LabError("B032_CACHE_SIZE_LIMIT")
                dst.parent.mkdir(parents=True, exist_ok=True)
                if dst.exists() or dst.is_symlink():
                    raise LabError("B032_CACHE_OVERWRITE_FORBIDDEN")
                src = tar.extractfile(member)
                if src is None:
                    raise LabError("B032_CACHE_ENTRY_UNREADABLE")
                with src, dst.open("xb") as out:
                    shutil.copyfileobj(src, out)
                counts["tectonic" if member.name.startswith("volumes/tectonic_cache/")
                       else "tiktoken"] += 1
    if counts["tectonic"] != 294 or counts["tiktoken"] != 1:
        raise LabError(f"B032_CACHE_COVERAGE_MISMATCH: {counts}")
    return counts["tectonic"], counts["tiktoken"]


def _mount(host: Path, target: str, *, readonly: bool = False) -> list[str]:
    spec = f"type=bind,source={host},target={target}"
    if readonly:
        spec += ",readonly"
    return ["--mount", spec]


def _container_command(repo: Path, workspace: Path, *, source: Path | None) -> list[str]:
    cmd = [
        "docker", "run", "--rm", "--pull", "never", "--network", "none",
        "--pids-limit", "256", "--cap-drop", "ALL",
        "--security-opt", "no-new-privileges", "--workdir", "/app",
        # The image's /app must stay writable so Docker can create /app/output,
        # /app/state etc. Mounting the whole checkout read-only at /app made
        # nested bind-mount targets fail during OCI initialization (exit 125).
        # Python imports current sources from /workspace, not old image /app.
        *_mount(repo, "/workspace", readonly=True),
        *_mount(workspace / "data", "/app/data"),
        *_mount(workspace / "output", "/app/output"),
        *_mount(workspace / "state", "/app/state"),
        *_mount(workspace / "cache", "/app/.cache/tectonic"),
    ]
    if source is not None:
        cmd += _mount(source, "/lab_source.pdf", readonly=True)
    env = {
        "APP_ROOT": "/app", "SQLITE_STATE_DIR": "/app/state",
        "GROQ_API_KEY": DUMMY_KEY, "GROQ_BASE_URL": "http://127.0.0.1:8080",
        "TPDF_OFFLINE_LAB": OPT_IN, "TPDF_FAKE_QUEUE_DB": "/app/state/queue.db",
        "IS_BENCHMARK": "0", "MAX_CONCURRENT_CHUNKS": "1",
        "MAX_GLOBAL_LLM_CONCURRENCY": "1", "GROQ_RPM_LIMIT": "1000",
        "GROQ_TPM_LIMIT": "200000", "PYTHONDONTWRITEBYTECODE": "1",
        # Prevent python -m from prepending /app, which already contains an
        # older image snapshot of the project. All subprocesses inherit this.
        "PYTHONPATH": "/workspace", "PYTHONSAFEPATH": "1",
        "TIKTOKEN_CACHE_DIR": "/app/data/tiktoken-cache",
        "COMPILER_OUTPUT_DIR": "/app/output",
        "XDG_CACHE_HOME": "/app/.cache/tectonic", "TECTONIC_CACHE_DIR": "/app/.cache/tectonic",
        "XDG_CONFIG_HOME": "/tmp/.config", "HOME": "/tmp",
        "HTTP_PROXY": "", "HTTPS_PROXY": "", "ALL_PROXY": "",
        "http_proxy": "", "https_proxy": "", "all_proxy": "",
        "NO_PROXY": "localhost,127.0.0.1", "no_proxy": "localhost,127.0.0.1",
    }
    for k, v in env.items():
        cmd.extend(("--env", k + "=" + v))
    cmd += ["--entrypoint", "python", RUNTIME_IMAGE,
            "-B", "-m", "apps.lab.offline_pdf_lab", "--inside-run"]
    if source is not None:
        cmd += ["--inside-source", "/lab_source.pdf"]
    return cmd


def _smoke_source(path: Path) -> None:
    import fitz
    with fitz.open() as doc:
        page = doc.new_page(width=595, height=842)
        page.insert_text((62, 88), "Scientific translation pipeline operational test", fontsize=16)
        sentences = [
            "The scientific method relies on observable evidence and careful measurement.",
            "Researchers record observations before drawing conclusions from the data.",
            "A reproducible process makes it easier to compare results across teams.",
            "This document is a laboratory fixture and contains no protected equations.",
        ]
        for i, sentence in enumerate(sentences):
            page.insert_text((62, 145 + 41 * i), sentence, fontsize=11)
        doc.save(str(path))


def _inside_run(*, source: str | None) -> int:
    """Bootstrap fresh DB, start in-process fake, then invoke B03 CLI as a subprocess."""
    if (os.environ.get("TPDF_OFFLINE_LAB") != OPT_IN or
            os.environ.get("GROQ_API_KEY") != DUMMY_KEY or
            os.environ.get("GROQ_BASE_URL") != "http://127.0.0.1:8080" or
            os.environ.get("SQLITE_STATE_DIR") != "/app/state"):
        raise LabError("B032_CONTAINER_ENV_NOT_ISOLATED")
    if (Path.cwd() != Path("/app") or not Path("/app/data").is_dir()
            or Path(__file__).resolve() != Path("/workspace/apps/lab/offline_pdf_lab.py")
            or os.environ.get("PYTHONPATH") != "/workspace"
            or os.environ.get("PYTHONSAFEPATH") != "1"):
        raise LabError("B032_CONTAINER_MOUNT_OR_CODE_DRIFT")
    from apps.lab.g3_fake import FakeServer, _Handler
    # /workspace is read-only; runtime data and code imports stay separate.
    subprocess.run([sys.executable, "-B", "-m", "infra.db.bootstrap"], check=True)
    db = Path("/app/state/queue.db")
    if not db.is_file():
        raise LabError("B032_BOOTSTRAP_QUEUE_MISSING")
    if source is None:
        pdf = Path("/app/data/offline_smoke.pdf")
        _smoke_source(pdf)
    else:
        pdf = Path(source)
        if pdf != Path("/lab_source.pdf"):
            raise LabError("B032_INVALID_SOURCE_PATH")
    server = FakeServer(("127.0.0.1", 8080), db, max_requests=128)
    thread = threading.Thread(target=server.serve_forever, daemon=True, name="b032_fake")
    thread.start()
    try:
        # Health check via loopback, no DNS or egress.
        from urllib.request import urlopen
        with closing(urlopen("http://127.0.0.1:8080/health", timeout=5)) as response:
            if response.status != 200:
                raise LabError("B032_FAKE_HEALTH_CHECK_FAILED")
        print("B032_FAKE_READY_LOOPBACK_OFFLINE", flush=True)
        result = subprocess.run([sys.executable, "-B", "-m", "apps.cli.main",
                                 "translate", str(pdf), "--run"], check=False)
        if result.returncode:
            raise LabError(f"B032_CLI_FAILED_EXIT_{result.returncode}")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
    sha = _sha(pdf)
    expected = Path("/app/output") / f"translated_{sha}.pdf"
    if not expected.is_file() or expected.stat().st_size < 8:
        raise LabError("B032_OUTPUT_PDF_MISSING")
    with expected.open("rb") as f:
        if f.read(5) != b"%PDF-":
            raise LabError("B032_OUTPUT_PDF_INVALID_HEADER")
    conn = sqlite3.connect("file:/app/state/fsm.db?mode=ro", uri=True)
    try:
        row = conn.execute("SELECT current_state, ast_hash FROM document_fsm WHERE document_id=?", (sha,)).fetchone()
    finally:
        conn.close()
    if row is None or row[0] != "COMPLETED":
        raise LabError("B032_FSM_NOT_COMPLETED")
    print(f"B032_VERIFIED_COMPLETE doc={sha} ast={row[1]} requests={server.requests}", flush=True)
    return 0


def _launch(root: Path, history: Path, *, source: Path | None,
            export_dir: Path) -> None:
    _check_checkout(root)
    _check_history(history)
    _docker_image_id()
    if source is not None and (not source.is_file() or source.is_symlink()):
        raise LabError("B032_SOURCE_PDF_NOT_READABLE")
    if source is not None:
        with source.open("rb") as f:
            if f.read(5) != b"%PDF-":
                raise LabError("B032_SOURCE_NOT_PDF")
    if shutil.disk_usage(tempfile.gettempdir()).free < 2 * 1024**3:
        raise LabError("B032_INSUFFICIENT_FREE_SPACE_2_GIB")
    # Unique lab directory, not a Docker volume or existing production path.
    workspace = Path(tempfile.mkdtemp(prefix="translator_pdf_b032_"))
    print("B032_LAB_DIR:", workspace, flush=True)
    for folder in ("data", "output", "state", "cache"):
        (workspace / folder).mkdir()
    cached = _seed_caches(history, workspace)
    print(f"B032_CACHE_SEEDED: tectonic={cached[0]} tiktoken={cached[1]}", flush=True)
    cmd = _container_command(root, workspace, source=source)
    # No shell, no build, no compose, no shared named volumes, no real egress.
    result = subprocess.run(cmd, check=False)
    if result.returncode:
        raise LabError(f"B032_CONTAINER_FAILED_EXIT_{result.returncode}; evidence_dir={workspace}")
    results = sorted((workspace / "output").glob("translated_*.pdf"))
    if len(results) != 1 or results[0].stat().st_size < 8:
        raise LabError("B032_PUBLISHED_PDF_COVERAGE_INVALID: " + str(workspace))
    with results[0].open("rb") as f:
        if f.read(5) != b"%PDF-":
            raise LabError("B032_INVALID_PDF_HEADER")
    export_dir.mkdir(parents=True, exist_ok=True)
    final = export_dir / ("OFFLINE_FAKE_" + results[0].name)
    if final.exists() or final.is_symlink():
        raise LabError("B032_EXPORT_ALREADY_EXISTS: " + str(final))
    with results[0].open("rb") as src, final.open("xb") as dst:
        shutil.copyfileobj(src, dst)
    print("B032_OPERATIONAL_PDF:", final, flush=True)
    print("B032_OPERATIONAL_PASS; LANGUAGE_TRANSLATION=FAKE_ECHO; SCIENTIFIC_FIDELITY=NOT_CERTIFIED", flush=True)
    print("B032_RETAINED_LAB_EVIDENCE:", workspace, flush=True)


def main(argv=None) -> None:
    p = argparse.ArgumentParser(description="B03.2 isolated offline PDF->PDF with in-container G3 fake")
    action = p.add_mutually_exclusive_group(required=True)
    action.add_argument("--preflight", action="store_true")
    action.add_argument("--run-smoke", action="store_true")
    action.add_argument("--run-pdf", type=Path)
    action.add_argument("--inside-run", action="store_true", help=argparse.SUPPRESS)
    p.add_argument("--inside-source", help=argparse.SUPPRESS)
    p.add_argument("--history-zip", type=Path, default=Path.home() / "Downloads" / HISTORY_ZIP)
    p.add_argument("--export-dir", type=Path, default=Path.home() / "Downloads" / "translator_pdf_offline")
    args = p.parse_args(argv)
    try:
        if args.inside_run:
            raise SystemExit(_inside_run(source=args.inside_source))
        root = Path(__file__).resolve().parents[2]
        if Path.cwd().resolve() != root:
            raise LabError("B032_RUN_FROM_REPO_ROOT")
        _check_checkout(root)
        history = args.history_zip.expanduser().resolve()
        _check_history(history)
        img = _docker_image_id()
        print("B032_PREFLIGHT_OK: image=" + img[:24] + " history=VERIFIED", flush=True)
        if args.preflight:
            print("B032_NO_WORKSPACE_WRITES_NO_CONTAINER_STARTED", flush=True)
            return
        source = args.run_pdf.resolve() if args.run_pdf is not None else None
        _launch(root, history, source=source, export_dir=args.export_dir.expanduser().resolve())
    except (LabError, OSError, subprocess.CalledProcessError, zipfile.BadZipFile,
            tarfile.TarError) as exc:
        print("B032_STOP: " + str(exc), file=sys.stderr)
        raise SystemExit(2) from exc


if __name__ == "__main__":
    main()
