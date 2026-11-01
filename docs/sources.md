# Data Sources Registry

## DDInter 2.0
- **Source**: DDInter (Drug-Drug Interaction Database)
- **Version / Release**: 2.0
- **URL**: http://ddinter.scbdd.com/
- **Download Date (UTC)**: 2026-10-31
- **Licence Checked**: CC BY-NC-SA 4.0 (Attribution-NonCommercial-ShareAlike 4.0 International)
- **Permitted Use**: Academic research prototype only; non-commercial redistribution
- **Attribution**: DDInter: a database of drug-drug interactions (http://ddinter.scbdd.com/)
- **Downloaded By**: Disha
- **Local Files**: `data/raw/ddinter/*.csv`
- **Notes / Exclusions / Subset Definition**:
  - Absence of an interaction record is not evidence of no interaction.
  - Synthetic evidence passages rendered with prefix `dd_` per canonicalized drug pair.
  - Held-out drug entities and text matches removed prior to final ID assignment.

## SemEval / Claim Gold Source
- **Source**: SemEval-2013 Task 9.1 Permitted Subset / Hand-labeled Fallback
- **Permitted Use**: Academic evaluation prototype
- **Exclusions**: DrugBank-derived XML documents are explicitly excluded per playbook terms.
- **Handled By**: Disha
- **Notes**: Fallback dataset generated using permitted openFDA interaction sentences and DDInter rows across 4 evaluation categories (SUPPORTED, CONTRADICTED, INSUFFICIENT_EVIDENCE, UNSUPPORTED).
