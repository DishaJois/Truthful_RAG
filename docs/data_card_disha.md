# Data Card Contributions — Disha

## 1. DDInter 2.0 Dataset & Processing Metrics

### Dataset Scope & Licence
- **Source**: DDInter 2.0 (Drug-Drug Interaction Database)
- **Licensing**: CC BY-NC-SA 4.0 (Non-Commercial, Attribution, Share-Alike)
- **Intended Use**: Academic prototype benchmark for truthful evidence retrieval and verification.

### Processing & Canonicalization Pipeline
1. **Pair Canonicalization**: Every interaction pair $(Drug_A, Drug_B)$ is sorted alphabetically to treat $(A, B)$ and $(B, A)$ identically, preventing duplicate symmetric interaction records.
2. **Held-Out Exclusions**: Drug pairs containing any entity on the 20-drug held-out list or its brand aliases are discarded. Furthermore, generated passages undergo case-insensitive whole-word matching to ensure no held-out drug name appears anywhere in the synthetic evidence text.
3. **Severity Handling**: 
   - Severity levels (`Major`, `Moderate`, `Minor`, etc.) are retained as distinct relation types (`interacts_with_<level>`) in the knowledge graph.
   - Records with `Unknown` severity are tracked and isolated to prevent skewing severity-dependent evaluation benchmarks.
4. **Synthetic Passage Rendering**:
   - Because DDInter provides tabular drug-drug associations rather than narrative text, each retained pair is converted into a structured synthetic evidence passage with the doc ID format `DDInter:<file>:row_<n>` and chunk prefix `dd_`.
   - *Limitation Note*: DDInter synthetic passages represent structured metadata renderings, not independent natural language clinical trials. Absence of a record does not imply absence of an interaction.

---

## 2. Risk Terms & Claim Gold Dataset

### Risk Terms Seed List (`risk_terms.json`)
- **Structure**: Divided into `high_risk` (e.g., *fatal*, *contraindicated*, *life-threatening*, *serotonin syndrome*) and `medium_risk` (e.g., *monitor*, *caution*, *dose adjustment*, *decreased clearance*).
- **Validation**: Seed terms were validated against real clinical interaction sentences to balance sensitive cue detection with low false-positive rates on standard interaction warnings.

### Claim Gold Dataset (`claim_gold.jsonl`)
- **Corpus Exclusions**: SemEval DrugBank-derived XML documents were explicitly excluded due to licensing/distribution constraints.
- **Fallback Implementation**: A curated set of 30 claims was constructed from permitted openFDA sentences and DDInter records, balanced across four target verification labels:
  - `SUPPORTED`: Claim accurately reflects interaction described in evidence.
  - `CONTRADICTED`: Claim asserts the exact opposite of what the evidence establishes.
  - `INSUFFICIENT_EVIDENCE`: Passage discusses the drugs but states interaction data is unknown, unstudied, or inconclusive.
  - `UNSUPPORTED`: Claim discusses an interaction entirely unaddressed by the cited evidence passage.
- **Audit & Review**: Each claim is accompanied by exact sentence-level provenance in `docs/claim_gold_audit.csv` with a verified audit status.
