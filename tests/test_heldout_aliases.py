import csv
import json

from src.data.openfda_process import (
    contains_heldout_word,
    find_matching_terms,
    run_pass2,
)


def test_heldout_files_match_finalized_reference_set():
    with open("docs/heldout_drugs.txt", encoding="utf-8-sig") as handle:
        canonical = {
            line.strip().lower()
            for line in handle
            if line.strip() and not line.lstrip().startswith("#")
        }
    with open("data/processed/aliases.json", encoding="utf-8-sig") as handle:
        aliases = json.load(handle)
    with open("docs/heldout_drug_aliases.txt", encoding="utf-8-sig") as handle:
        alias_lines = {
            line.strip().lower()
            for line in handle
            if line.strip() and not line.lstrip().startswith("#")
        }
    assert len(canonical) == 20
    assert canonical.issubset(set(alias_lines))
    assert aliases["paracetamol"] == "acetaminophen"
    assert aliases["salbutamol"] == "albuterol"


def test_phrase_matching_handles_multiword_and_punctuation_aliases():
    terms = {"drizalma sprinkle", "toprol xl", "st. john's wort"}
    assert find_matching_terms("DRIZALMA Sprinkle delayed release", terms) == {"drizalma sprinkle"}
    assert find_matching_terms("Uses Toprol-XL daily", terms) == {"toprol xl"}
    assert contains_heldout_word("Avoid St. John's wort products", terms)
    assert not contains_heldout_word("The patient takes warfarin", terms)


def test_brand_aliases_map_to_canonical_generic_names():
    with open("data/processed/aliases.json", encoding="utf-8-sig") as handle:
        aliases = json.load(handle)
    assert aliases["coumadin"] == "warfarin"
    assert aliases["advil"] == "ibuprofen"
    assert aliases["toprol-xl"] == "metoprolol"


def test_pass2_excludes_aliases_and_heldout_primary_labels(tmp_path):
    intermediate = tmp_path / "input.jsonl"
    drugs = tmp_path / "drugs.json"
    heldout = tmp_path / "heldout.txt"
    aliases = tmp_path / "aliases.txt"
    chunks = tmp_path / "chunks.jsonl"
    triples = tmp_path / "triples.csv"

    intermediate.write_text(
        "\n".join(
            json.dumps(row)
            for row in [
                {"doc_id": "keep", "primary_drug": "warfarin", "text": "Warfarin and aspirin are discussed."},
                {"doc_id": "alias", "primary_drug": "warfarin", "text": "Patient uses Toprol-XL."},
                {"doc_id": "heldout-primary", "primary_drug": "metoprolol", "text": "Warfarin and aspirin are discussed."},
            ]
        ),
        encoding="utf-8",
    )
    drugs.write_text(json.dumps(["warfarin", "aspirin"]), encoding="utf-8")
    heldout.write_text("metoprolol\n", encoding="utf-8")
    aliases.write_text("toprol xl\n", encoding="utf-8")

    run_pass2(str(intermediate), "TEST", str(drugs), str(aliases), str(chunks), str(triples), str(heldout))
    with chunks.open(encoding="utf-8") as handle:
        kept_chunks = [json.loads(line) for line in handle]
    assert [chunk["doc_id"] for chunk in kept_chunks] == ["keep"]
    with triples.open(encoding="utf-8", newline="") as handle:
        assert len(list(csv.DictReader(handle))) == 1


def test_kg_contains_no_heldout_entities_or_evidence():
    from src.data.openfda_process import build_term_trie, load_heldout, match_trie

    terms = load_heldout("docs/heldout_drugs.txt", "docs/heldout_drug_aliases.txt")
    trie = build_term_trie(terms)
    with open("data/kg/triples.csv", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert rows
    assert not any(match_trie(row["subject"], trie) or match_trie(row["object"], trie) for row in rows)

    from src.kg.build_kg import load_chunks
    chunk_text = {key: value for key, value in load_chunks().items()}
    checked_ids = {row["chunk_id"] for row in rows}
    assert all(not match_trie(chunk_text[chunk_id], trie) for chunk_id in checked_ids)
