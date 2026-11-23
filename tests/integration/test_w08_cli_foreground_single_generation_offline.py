"""W08-2c: one offline CLI->OCR->G3->G5 foreground composition witness.

Use real CLI admission, OCR Router orchestration, context persistence, G3
claim/staging/publication, G5 assembly authority and independently reopened
SQLite. Only isolate PDF parsing, external LLM transport and Tectonic execution.
Neither the synthetic response nor compiled page certifies translation/science.
"""
from __future__ import annotations

from contextlib import closing
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
import sys
from types import SimpleNamespace
from typing import Any

import fitz
import pytest

from apps.cli import main as cli
from core.ast.enums import ContentNodeType, HeadingLevel
from core.ast.hashing import compute_ast_hash
from core.ast.models import ASTNode, HeadingPayload, ParagraphPayload, TranslationTaskType
from core.chunking.manifest_contract import ChunkPlan
from infra.db.context_snapshot_repo import DurableContextPlanRepository
from infra.db.control_repo import ControlPlaneRepository


ROOT = Path(__file__).resolve().parents[2]


class _ControlledParser:
    """The only nonreal OCR dependency; supplies typed, deterministic nodes."""

    def parse(self, pdf_path: str) -> list[ASTNode]:
        with fitz.open(pdf_path) as document:
            assert document.page_count == 1
        return [
            ASTNode(node_id="h_methods", sequence_id=1,
                    node_type=ContentNodeType.HEADING,
                    payload=HeadingPayload(content="Methods",
                                           heading_level=HeadingLevel.H1)),
            ASTNode(node_id="p_methods", sequence_id=2,
                    node_type=ContentNodeType.PARAGRAPH,
                    payload=ParagraphPayload(content="Alpha sample.")),
            ASTNode(node_id="h_results", sequence_id=3,
                    node_type=ContentNodeType.HEADING,
                    payload=HeadingPayload(content="Results",
                                           heading_level=HeadingLevel.H1)),
            ASTNode(node_id="p_results", sequence_id=4,
                    node_type=ContentNodeType.PARAGRAPH,
                    payload=ParagraphPayload(content="Beta sample.")),
        ]


class _OfflineProvider:
    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple[str, ...]]] = []

    async def translate(self, envelope: Any) -> Any:
        # Execute the real PromptBuilder and bridge. Only the HTTP transport is
        # replaced; parse the effective prompt's G3 protocol, not a fabricated plan.
        breadcrumbs = tuple(envelope.schema.context.breadcrumbs)
        self.calls.append((envelope.chunk_id, breadcrumbs))
        protocol = json.loads(envelope.schema.payload.content)
        binding = protocol["response_binding"]
        members = [
            {
                "node_id": m["node_id"],
                "segment_index": m["segment_index"],
                "source_sha256": m["source_sha256"],
                "translated_text": "SYNTHETIC_" + m["source_text"],
            }
            for m in protocol["members"]
        ]
        raw = json.dumps(
            {**binding, "members": members},
            ensure_ascii=False, sort_keys=True, separators=(",", ":"),
        )
        return SimpleNamespace(chunk_id=envelope.chunk_id, content=raw)


@pytest.mark.integration
def test_cli_foreground_context_receipts_projections_and_pdf_same_generation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    from apps.bootstrap import pipeline_factory
    from apps.compiler.tectonic_runner import HostTectonicRunner
    from core.ast.registry import ASTRegistry
    from infra.db import connection
    from runtime import engine
    from apps.llm_workers.sync_bridge import SyncProviderBridge
    from apps.llm_workers.prompt_builder import PromptBuilder
    from core.finops.measurement import InferenceMeasurementService
    from core.validation.estimators import ExactBPEEstimator
    from core.validation.budget import PromptBudgetCalculator, StandardCompressionPolicy
    from apps.llm_workers.g3_admission import G3PreEffectAdmission
    from decimal import Decimal

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(connection, "BASE_DIR", tmp_path)
    monkeypatch.setenv("APP_ROOT", str(tmp_path))
    monkeypatch.setenv("COMPILER_OUTPUT_DIR", str(tmp_path / "output"))
    monkeypatch.setenv("IS_BENCHMARK", "0")
    monkeypatch.setenv("MAX_CONCURRENT_CHUNKS", "1")
    monkeypatch.delenv("SQLITE_STATE_DIR", raising=False)

    state_dir = tmp_path / "infra" / "db"
    state_dir.mkdir(parents=True)
    # Physical schemas on disposable SQLite; no bootstrap on real paths.
    for filename, schema in (
        ("fsm.db", "schema_fsm.sql"),
        ("queue.db", "schema_queue.sql"),
        ("materialized.db", "schema_materialized.sql"),
    ):
        with closing(sqlite3.connect(state_dir / filename)) as conn:
            conn.executescript(
                (ROOT / "infra" / "db" / schema).read_text(encoding="utf-8")
            )
            conn.commit()

    source = tmp_path / "source.pdf"
    with fitz.open() as pdf:
        page = pdf.new_page()
        page.insert_text((72, 72), "Methods")
        page.insert_text((72, 98), "Alpha sample.")
        page.insert_text((72, 150), "Results")
        page.insert_text((72, 176), "Beta sample.")
        pdf.save(source)
    document_id = sha256(source.read_bytes()).hexdigest()

    monkeypatch.setattr(
        pipeline_factory, "build_extraction_pipeline", lambda: _ControlledParser(),
    )
    # The real G5 CompilationService renders the selected EN->ES content;
    # only the external Tectonic binary is replaced with a one-page PDF.
    rendered_tex: list[str] = []
    def fake_compile(
        _self: HostTectonicRunner, tex_content: str, output_dir: str,
        output_filename: str = "output.pdf", *, image_assets: Any = (),
    ) -> str:
        assert "\\begin{document}" in tex_content
        rendered_tex.append(tex_content)
        assert not image_assets
        target = Path(output_dir) / output_filename
        with fitz.open() as pdf:
            page = pdf.new_page()
            page.insert_text((72, 72), "Controlled compiler witness")
            pdf.save(target)
        return str(target)

    monkeypatch.setattr(HostTectonicRunner, "compile", fake_compile)
    import apps.cli.pdf_product as product
    monkeypatch.setattr(product.shutil, "which", lambda name: "test-tectonic" if name == "tectonic" else None)

    provider = _OfflineProvider()
    processors = []

    def fake_processor_factory(context_snapshots: Any) -> tuple[Any, Any]:
        estimator = ExactBPEEstimator()
        builder = PromptBuilder(
            model_name="offline-fake", prompt_version="w08-offline",
            measurement_service=InferenceMeasurementService(estimator=estimator),
            budget_calculator=PromptBudgetCalculator(
                primary_window_limit=8192, fallback_window_limit=1048576,
                min_output_reserve=256, max_output_reserve=4096,
            ),
            compression_policy=StandardCompressionPolicy(),
        )
        # Synthetic, offline-only approvals for the fake provider; never use
        # these references as real destination or monetary authorization.
        offline_policy = G3PreEffectAdmission(
            provider_id="offline-test", model_name="offline-fake",
            root_config_sha256=engine._product_effective_config_sha256(),
            input_limit=32768, output_limit=4096, context_window=65536,
            input_estimator=estimator, estimator_evidence_ref="FAKE_OFFLINE_ESTIMATOR",
            egress_authorization_ref="FAKE_OFFLINE_EGRESS",
            data_scope_ref="FAKE_OFFLINE_DATA_SCOPE",
            purpose_ref="FAKE_OFFLINE_EN_ES",
            retention_ref="FAKE_OFFLINE_RETENTION",
            training_use_ref="FAKE_OFFLINE_TRAINING",
            budget_authorization_ref="FAKE_OFFLINE_BUDGET",
            price_evidence_ref="FAKE_OFFLINE_PRICING",
            input_price_per_token=Decimal("0"),
            output_price_per_token=Decimal("0"),
            authorized_max_cost=Decimal("0"),
        )
        bridge = SyncProviderBridge(
            provider, builder, context_snapshots=context_snapshots,
            effective_config_sha256=engine._product_effective_config_sha256(),
            source_language="en", target_language="es", provider_id="offline-test",
            pre_effect_admission=offline_policy,
        )
        processors.append(bridge)
        return bridge, SimpleNamespace(close=lambda: None)

    monkeypatch.setattr(engine, "_create_chunk_processor", fake_processor_factory)
    monkeypatch.setattr(
        sys, "argv", ["apps.cli.main", "translate", str(source), "--run"],
    )

    # Actual public CLI command drives actual OCR, G3 and G5 composition roots.
    cli.main()

    with (
        closing(sqlite3.connect(state_dir / "fsm.db")) as fsm,
        closing(sqlite3.connect(state_dir / "queue.db")) as queue,
        closing(sqlite3.connect(state_dir / "materialized.db")) as materialized,
    ):
        status = fsm.execute(
            "SELECT ast_hash,current_state,is_terminal FROM document_fsm "
            "WHERE document_id=?", (document_id,),
        ).fetchone()
        assert status is not None and status[1:] == ("COMPLETED", 1)
        ast_hash = status[0]
        persisted_ast = ASTRegistry(workspace_dir=str(tmp_path)).get_document_ast(
            document_id, ast_hash,
        )
        assert len(persisted_ast) == 4
        assert compute_ast_hash(persisted_ast) == ast_hash
        plan, snapshots = DurableContextPlanRepository(
            ControlPlaneRepository(queue),
        ).load_verified(document_id, ast_hash, persisted_ast)
        assert isinstance(plan, ChunkPlan)
        units = [u for u in plan.units if u.chunk_type == TranslationTaskType.TRANSLATE]
        # W4.2: both accredited headings AND their paragraphs now receive
        # distinct translation units. The headings share the verified root
        # snapshot; the paragraphs retain their individual H1 contexts.
        assert len(units) == 4 and len(snapshots) == 3
        by_node = {u.members[0].node_id: u for u in units}
        assert set(by_node) == {
            "h_methods", "p_methods", "h_results", "p_results",
        }
        assert all(len(u.members) == 1 for u in units)
        assert (
            by_node["h_methods"].context_id
            == by_node["h_results"].context_id
        )
        assert by_node["p_methods"].context_id != by_node["p_results"].context_id
        assert all(u.context_id in snapshots for u in units)
        root = snapshots[by_node["h_methods"].context_id]
        assert len(root.breadcrumbs) == 1
        assert root.breadcrumbs[0].level == 0
        assert root.breadcrumbs[0].title == "[ROOT_DOCUMENT_CONTEXT]"
        assert len(provider.calls) == 4
        assert {chunk for chunk, _ in provider.calls} == {
            u.chunk_id for u in units
        }
        assert {context for _, context in provider.calls} == {
            ("[ROOT_DOCUMENT_CONTEXT]",),
            ("H1: Methods",), ("H1: Results",),
        }

        rows = queue.execute(
            "SELECT chunk_id, raw_response, execution_id, generation_sha256, root_config_sha256, generation_binding_sha256 FROM chunk_result_receipts "
            "WHERE document_id=? AND ast_hash=?",
            (document_id, ast_hash),
        ).fetchall()
        assert len(rows) == len(plan.units) == 4
        assert sum(raw is not None for _, raw, _, _, _, _ in rows) == 4
        assert all(execution_id for _, _, execution_id, _, _, _ in rows)
        assert all(
            (generation is not None and len(generation) == 64
             and root == engine._product_effective_config_sha256()
             and binding is not None and len(binding) == 64)
            if raw is not None else generation is None and root is None and binding is None
            for _, raw, _, generation, root, binding in rows
        )

        projections = materialized.execute(
            "SELECT node_id, normalized_response FROM valid_chunks_cache "
            "WHERE document_id=? AND ast_hash=?", (document_id, ast_hash),
        ).fetchall()
        assert {node for node, _ in projections} == {
            "h_methods", "p_methods", "h_results", "p_results",
        }
        assert dict(projections) == {
            "h_methods": "SYNTHETIC_Methods",
            "p_methods": "SYNTHETIC_Alpha sample.",
            "h_results": "SYNTHETIC_Results",
            "p_results": "SYNTHETIC_Beta sample.",
        }
        pub = materialized.execute(
            "SELECT manifest_sha256 FROM g3_plan_publications "
            "WHERE document_id=? AND ast_hash=?", (document_id, ast_hash),
        ).fetchone()
        assert pub == (plan.digest,)

    result = tmp_path / "output" / f"translated_{document_id}.pdf"
    assert result.is_file()
    with fitz.open(result) as compiled:
        assert compiled.page_count == 1
    assert len(rendered_tex) == 1
    assert r"\section*{SYNTHETIC\_Methods}" in rendered_tex[0]
    assert r"\section*{SYNTHETIC\_Results}" in rendered_tex[0]
    assert r"SYNTHETIC\_Alpha sample." in rendered_tex[0]
    assert r"SYNTHETIC\_Beta sample." in rendered_tex[0]
    assert processors
