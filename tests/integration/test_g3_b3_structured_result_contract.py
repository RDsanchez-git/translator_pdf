"""G3-B3/1: structured member responses and full-node pure recomposition.

No provider, daemon, physical PDF, database, or network calls.
"""
from dataclasses import replace
from hashlib import sha256
import json

import pytest

from core.ast.models import ASTNode, ParagraphPayload, MathPayload, TablePayload
from core.ast.enums import ContentNodeType, TranslationStrategy
from core.ast.grouper import SemanticGroup
from core.chunking.semantic_chunking import TokenBudgetChunker, ChunkPolicy
from core.chunking.manifest_contract import ChunkPlan
from core.chunking.result_contract import parse_chunk_response, materialize_node_results


class _Estimator:
    def estimate_tokens(self, text):
        return len(text.split())


def _node(node_id, seq, text, kind=ContentNodeType.PARAGRAPH,
          strategy=TranslationStrategy.TRANSLATE):
    cls = {ContentNodeType.DISPLAY_EQUATION: MathPayload,
           ContentNodeType.TABLE_SIMPLE: TablePayload}.get(kind, ParagraphPayload)
    return ASTNode(node_id=node_id, sequence_id=seq, node_type=kind,
                   strategy=strategy, payload=cls(content=text))


def _plan(ast, budget=30, doc="doc_b3", generation="ast_b3"):
    units = TokenBudgetChunker(_Estimator(), ChunkPolicy(max_tokens=budget, prompt_overhead_tokens=0)).chunk_group(
        SemanticGroup(structural_path=(), context_id="ctx", nodes=ast), 1,
    )
    return ChunkPlan.build(doc, generation, ast, units)


def _response(plan, unit, translations=None):
    translations = translations or {}
    return {
        "schema_version": 1,
        "document_id": plan.document_id,
        "ast_hash": plan.ast_hash,
        "manifest_sha256": plan.digest,
        "chunk_id": unit.chunk_id,
        "members": [
            {"node_id": m.node_id, "segment_index": m.segment_index,
             "source_sha256": sha256(m.source_text.encode("utf-8")).hexdigest(),
             "translated_text": translations.get((m.node_id, m.segment_index), "Traducido.")}
            for m in unit.members
        ],
    }


def _json(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


def test_two_nodes_one_chunk_response_order_is_identity_based_not_positional():
    p = _plan([_node("a", 1, "Alpha."), _node("b", 2, "Beta.")])
    assert len(p.units) == 1
    unit = p.units[0]
    response = _response(p, unit, {("a", 0): "Alfa.", ("b", 0): "Beta traducida."})
    response["members"].reverse()
    parsed = parse_chunk_response(p, unit.chunk_id, _json(response))
    assert [m.node_id for m in parsed.members] == ["a", "b"]
    result = materialize_node_results(p, {unit.chunk_id: _json(response)})
    assert [(m.node_id, m.text) for m in result] == [("a", "Alfa."), ("b", "Beta traducida.")]
    assert [m.chunk_ids for m in result] == [(unit.chunk_id,), (unit.chunk_id,)]
    assert all(m.document_id == p.document_id and m.ast_hash == p.ast_hash for m in result)
    assert result[0].text_sha256 == sha256("Alfa.".encode()).hexdigest()


def test_fragments_across_chunks_reassemble_without_added_delimiters():
    p = _plan([_node("parent", 1, "Alpha first sentence. Beta second sentence. Gamma third sentence.")], budget=4)
    assert len(p.units) == 3
    responses = {}
    translated = ["Primera frase.", "Segunda frase.", "Tercera frase."]
    for unit in p.units:
        fragment = unit.members[0]
        responses[unit.chunk_id] = _json(_response(p, unit, {("parent", fragment.segment_index): translated[fragment.segment_index]}))
    result = materialize_node_results(p, responses)
    assert len(result) == 1
    assert result[0].node_id == "parent"
    assert result[0].text == "Primera frase. Segunda frase. Tercera frase."
    assert result[0].chunk_ids == tuple(u.chunk_id for u in p.units)


def test_preserve_is_bypassed_and_partial_remains_explicit():
    p = _plan([
        _node("txt", 1, "Translate me."),
        _node("math", 2, r"E=mc^2", kind=ContentNodeType.DISPLAY_EQUATION,
              strategy=TranslationStrategy.PASSTHROUGH),
        _node("table", 3, "| a | b |", kind=ContentNodeType.TABLE_SIMPLE),
        _node("omitted", 4, "discard", strategy=TranslationStrategy.OMIT),
    ])
    assert len(p.units) == 3
    response_units = [u for u in p.units if u.chunk_type.value != "preserve"]
    responses = {u.chunk_id: _json(_response(p, u, {
        ("txt", 0): "Traducime.", ("table", 0): "| uno | dos |",
    })) for u in response_units}
    result = materialize_node_results(p, responses)
    assert [(m.node_id, m.text) for m in result] == [
        ("txt", "Traducime."), ("math", r"E=mc^2"), ("table", "| uno | dos |"),
    ]
    preserve = next(u for u in p.units if u.chunk_type.value == "preserve")
    with pytest.raises(ValueError, match="PRESERVE_RESPONSE_FORBIDDEN"):
        parse_chunk_response(p, preserve.chunk_id, "{}")
    with pytest.raises(ValueError, match="CHUNK_RESPONSE_COVERAGE_MISMATCH"):
        materialize_node_results(p, {**responses, preserve.chunk_id: "{}"})


def test_only_preserve_nodes_materialize_without_provider_results():
    p = _plan([_node("math", 1, r"\\alpha + \\beta", kind=ContentNodeType.DISPLAY_EQUATION)])
    result = materialize_node_results(p, {})
    assert len(result) == 1 and result[0].text == r"\\alpha + \\beta"


@pytest.mark.parametrize("mutation,marker", [
    (lambda r: r["members"].pop(), "MEMBER_COVERAGE_MISMATCH"),
    (lambda r: r["members"].append(dict(r["members"][0])), "MEMBER_COVERAGE_MISMATCH"),
    (lambda r: r["members"][1].update(node_id="unknown"), "UNEXPECTED_MEMBER"),
    (lambda r: r["members"][1].update(node_id="a"), "DUPLICATE_MEMBER"),
    (lambda r: r["members"][0].update(source_sha256="0" * 64), "SOURCE_HASH_MISMATCH"),
    (lambda r: r.update(manifest_sha256="0" * 64), "RESPONSE_BINDING_MISMATCH"),
    (lambda r: r.update(ast_hash="wrong"), "RESPONSE_BINDING_MISMATCH"),
    (lambda r: r.update(document_id="wrong"), "RESPONSE_BINDING_MISMATCH"),
    (lambda r: r.update(chunk_id="other"), "RESPONSE_BINDING_MISMATCH"),
    (lambda r: r.update(schema_version=2), "UNSUPPORTED_RESPONSE_SCHEMA"),
    (lambda r: r.update(schema_version=True), "UNSUPPORTED_RESPONSE_SCHEMA"),
    (lambda r: r.update(extra=1), "INVALID_RESPONSE_ENVELOPE"),
    (lambda r: r["members"][0].update(extra=1), "INVALID_MEMBER_ENVELOPE"),
    (lambda r: r["members"][0].update(segment_index=True), "INVALID_MEMBER_TYPES"),
    (lambda r: r["members"][0].update(translated_text=""), "EMPTY_TRANSLATION"),
    (lambda r: r["members"][0].update(translated_text="  "), "EMPTY_TRANSLATION"),
    (lambda r: r["members"][0].update(translated_text=" texto"), "TRANSLATION_BOUNDARY_WHITESPACE"),
])
def test_invalid_member_responses_fail_closed(mutation, marker):
    p = _plan([_node("a", 1, "Alpha."), _node("b", 2, "Beta.")])
    u = p.units[0]
    r = _response(p, u)
    mutation(r)
    with pytest.raises(ValueError, match=marker):
        parse_chunk_response(p, u.chunk_id, _json(r))


@pytest.mark.parametrize("raw,marker", [
    ('{"schema_version":1,"schema_version":1}', "DUPLICATE_JSON_KEY"),
    ('{"a":{"key":1,"key":2}}', "DUPLICATE_JSON_KEY"),
    ("NaN", "INVALID_JSON_CONSTANT"),
    ("not valid json", "INVALID_RESPONSE_JSON"),
    ("[]", "INVALID_RESPONSE_ENVELOPE"),
    (None, "RESPONSE_MUST_BE_JSON_TEXT"),
])
def test_invalid_json_is_rejected(raw, marker):
    p = _plan([_node("a", 1, "Alpha.")])
    with pytest.raises(ValueError, match=marker):
        parse_chunk_response(p, p.units[0].chunk_id, raw)


def test_unknown_chunk_rejected_before_payload_parse():
    p = _plan([_node("a", 1, "Alpha.")])
    with pytest.raises(ValueError, match="UNKNOWN_CHUNK"):
        parse_chunk_response(p, "not_in_plan", "{}")


def test_incomplete_or_extra_chunks_never_return_partial_nodes():
    p = _plan([_node("one", 1, "Alpha first sentence. Beta second sentence.")], budget=4)
    assert len(p.units) == 2
    response = {p.units[0].chunk_id: _json(_response(p, p.units[0]))}
    with pytest.raises(ValueError, match="CHUNK_RESPONSE_COVERAGE_MISMATCH"):
        materialize_node_results(p, response)
    response[p.units[1].chunk_id] = _json(_response(p, p.units[1]))
    response["unknown"] = "{}"
    with pytest.raises(ValueError, match="CHUNK_RESPONSE_COVERAGE_MISMATCH"):
        materialize_node_results(p, response)


def test_source_boundary_whitespace_preserved_through_segmented_translation():
    p = _plan([_node("paragraph", 1, "\n Alpha. Beta. \n")], budget=1)
    assert len(p.units) == 2
    responses = {u.chunk_id: _json(_response(p, u, {
        ("paragraph", 0): "Alfa.", ("paragraph", 1): "Beta traducida.",
    })) for u in p.units}
    assert materialize_node_results(p, responses)[0].text == "\n Alfa. Beta traducida. \n"


def test_whitespace_only_source_never_silently_disappears_in_translation():
    p = _plan([_node("blank", 1, "  \n ")])
    u = p.units[0]
    with pytest.raises(ValueError, match="WHITESPACE_ONLY_SOURCE"):
        materialize_node_results(p, {u.chunk_id: _json(_response(p, u))})


def test_response_size_bound_rejects_uncontrolled_payload():
    p = _plan([_node("a", 1, "Alpha.")])
    with pytest.raises(ValueError, match="RESPONSE_TOO_LARGE"):
        parse_chunk_response(p, p.units[0].chunk_id, "x" * (4 * 1024 * 1024 + 1))


def test_translated_unicode_surrogates_rejected_before_projection():
    p = _plan([_node("a", 1, "Alpha.")])
    u = p.units[0]
    r = _response(p, u)
    r["members"][0]["translated_text"] = "\ud800"
    with pytest.raises(ValueError, match="INVALID_UNICODE"):
        parse_chunk_response(p, u.chunk_id, json.dumps(r))
