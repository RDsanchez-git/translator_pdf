# core/prompting/canonicalizer.py
import json
import hashlib
from core.prompting.models import PromptSchema

class PromptCanonicalizer:
    @staticmethod
    def to_canonical_json(schema: PromptSchema) -> str:
        raw_dict = schema.model_dump(mode='json', exclude_none=True)
        return json.dumps(raw_dict, sort_keys=True, separators=(',', ':'), ensure_ascii=False)

    @staticmethod
    def compute_hash(schema: PromptSchema) -> str:
        canonical_str = PromptCanonicalizer.to_canonical_json(schema)
        return hashlib.sha256(canonical_str.encode('utf-8')).hexdigest()