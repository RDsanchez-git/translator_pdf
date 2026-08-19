import hashlib
import json
import time
import logging
from queue import Full
from threading import Lock
from typing import List, Optional, Any, Dict

from core.ast.models import (
    ASTNode, HeadingPayload, ParagraphPayload, MathPayload, 
    CodePayload, TablePayload, ListPayload
)
from core.ast.enums import ContentNodeType
from core.normalization.base import NormalizationReport, NormalizerTrace, NormalizationEvent, WarningEntry
from core.normalization.registry import NormalizationPolicyRegistry, NormalizationPolicy

logger = logging.getLogger(__name__)

class NormalizationPipeline:
    def __init__(self, telemetry_queue: Optional[Any] = None, version: str = "1.0.0"):
        self._version = version
        self._registry = NormalizationPolicyRegistry.get_instance()
        self._telemetry_queue = telemetry_queue
        self._dropped_lock = Lock()
        self._dropped_telemetry_events = 0

    @property
    def dropped_events_count(self) -> int:
        with self._dropped_lock:
            return self._dropped_telemetry_events

    def _compute_deterministic_hash(self, text: str, policy: Optional[NormalizationPolicy]) -> str:
        content_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        payload = {
            "dnl_version": self._version,
            "policy_id": policy.policy_id if policy else "PASSTHROUGH",
            "normalizers": [n.signature for n in policy.normalizers] if policy else [],
            "content_hash": content_hash
        }
        json_payload = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(json_payload.encode("utf-8")).hexdigest()

    def process_node(self, node: ASTNode) -> NormalizationReport:
        canonical_key = node.node_type.value
        policy = self._registry.get_policy_for_type(canonical_key)
        
        current_text = node.text_content or ""
        current_hash = self._compute_deterministic_hash(current_text, policy)
        
        stored_hash = node.control_plane.get("normalization_hash")
        if stored_hash == current_hash:
            return NormalizationReport(node=node, changed=False)

        if not policy or not policy.normalizers:
            new_cp = dict(node.control_plane)
            new_cp["normalization_hash"] = current_hash
            new_cp["normalization_timestamp"] = time.time()
            
            cloned_node = node.model_copy(update={"control_plane": new_cp})
            return NormalizationReport(node=cloned_node, changed=False)

        working_text = current_text
        traces: List[NormalizerTrace] = []
        consolidated_metrics: Dict[str, int] = {}
        warnings: List[WarningEntry] = []
        hard_fails: List[str] = []
        has_mutations = False

        for normalizer in policy.normalizers:
            result = normalizer.normalize(working_text)
            
            if result.fixes:
                working_text = result.text
                traces.append(NormalizerTrace(normalizer.normalizer_id, result.fixes))
                consolidated_metrics[normalizer.normalizer_id] = len(result.fixes)
                has_mutations = True
                
            if result.warnings:
                warnings.extend(result.warnings)
            if result.hard_fails:
                hard_fails.extend(result.hard_fails)
                break

        final_hash = self._compute_deterministic_hash(working_text, policy)
        new_cp = dict(node.control_plane)
        new_cp["normalization_hash"] = final_hash
        new_cp["normalization_timestamp"] = time.time()

        if has_mutations:
            if node.node_type == ContentNodeType.HEADING:
                from core.ast.enums import HeadingLevel
                old_level = node.payload.heading_level if isinstance(node.payload, HeadingPayload) else HeadingLevel.UNKNOWN
                new_payload = HeadingPayload(content=working_text, heading_level=old_level)
            elif node.node_type in (ContentNodeType.PARAGRAPH, ContentNodeType.CAPTION):
                new_payload = ParagraphPayload(content=working_text)
            elif node.node_type in (ContentNodeType.DISPLAY_EQUATION, ContentNodeType.INLINE_EQUATION):
                new_payload = MathPayload(content=working_text)
            elif node.node_type == ContentNodeType.CODE:
                new_payload = CodePayload(content=working_text)
            elif node.node_type in (ContentNodeType.TABLE_SIMPLE, ContentNodeType.TABLE_COMPLEX):
                new_payload = TablePayload(content=working_text)
            elif node.node_type == ContentNodeType.LIST:
                new_payload = ListPayload(content=working_text)
            else:
                new_payload = ParagraphPayload(content=working_text)

            updated_node = node.model_copy(update={"payload": new_payload, "control_plane": new_cp})
        else:
            updated_node = node.model_copy(update={"control_plane": new_cp})

        if has_mutations and self._telemetry_queue:
            event = NormalizationEvent(
                node_id=node.node_id,
                node_type=canonical_key,
                changed=True,
                metrics_json=json.dumps(consolidated_metrics),
                traces_json=json.dumps([{"id": t.normalizer_id, "fixes": t.fixes} for t in traces]),
                timestamp=time.time()
            )
            try:
                self._telemetry_queue.put_nowait(event)
            except Full:
                with self._dropped_lock:
                    self._dropped_telemetry_events += 1
                logger.warning(f"TELEMETRY_DROP: Queue full. Total dropped: {self._dropped_telemetry_events}")

        return NormalizationReport(
            node=updated_node,
            changed=has_mutations,
            traces=traces,
            metrics=consolidated_metrics,
            warnings=warnings,
            hard_fails=hard_fails
        )

    def process_batch(self, nodes: List[ASTNode]) -> List[NormalizationReport]:
        return [self.process_node(node) for node in nodes]