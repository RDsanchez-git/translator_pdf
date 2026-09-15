# DF-04 Benchmark: ZhangShasha vs APTED

**Corpus version:** v1.0
**Total documents:** 6
**Criterion threshold:** 1.00%

## Results

| Metric | Value |
|--------|-------|
| Average divergence | 8.5585% |
| Max divergence | 22.6293% |
| Criterion met | ❌ No |
| Decision | Investigar causa raíz y documentar |

## Per-document comparison

| Document | ZhangShasha | APTED | Divergence |
|----------|:-----------:|:-----:|:----------:|
| doc_01_single | 0.5571 | 0.4357 | 12.1429% |
| doc_02_double | 0.5259 | 0.2996 | 22.6293% |
| doc_03_math | 0.7963 | 0.8025 | 0.6173% |
| doc_04_table | 0.7538 | 0.6231 | 13.0769% |
| doc_05_graph | 0.7692 | 0.7404 | 2.8846% |
| doc_07_pesaran | 1.0000 | 1.0000 | 0.0000% |

## Known differences

| Aspect | ZhangShasha | APTED |
|--------|-------------|-------|
| Cost model | UnitCostContext (uniform) | CostMatrix.default_v1 (diff substitution) |
| Normalization | MaxBound: 1-TED/max(gt,cand) | 1-TED/(del*gt+ins*cand) |
| Fingerprint | No .strip() | .strip() applied (H-5.2-6) |
