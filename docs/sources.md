# Data Sources Registry

## openFDA Drug Labels
- **Source**: U.S. FDA openFDA drug product labels
- **Data APIs**: https://open.fda.org/apis/drug/label/
- **Terms / Usage**: https://open.fda.org/terms/
- **Download Date (UTC)**: 2026-10-31
- **Licence/Terms Checked**: openFDA data is provided under the openFDA terms of service; verify
  the current terms before redistribution or public deployment.
- **Permitted Use**: Academic, reproducible research and software prototyping
- **Attribution**: "Source: openFDA drug label data" with the FDA and openFDA references
- **Local Files**: `data/raw/openfda/*.zip`, processed chunks and triple files
- **Notes**: Drug-label text is evidence, not a substitute for prescriber or pharmacist guidance.
  Availability of a product label does not establish the completeness or currency of interaction data.

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
