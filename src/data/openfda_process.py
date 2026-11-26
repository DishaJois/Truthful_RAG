import argparse
import csv
import hashlib
import json
import os
import re
import zipfile
from pathlib import Path
from typing import Dict, List, Set

def load_heldout(heldout_path: str, aliases_path: str) -> Set[str]:
    heldout = set()
    for path in [heldout_path, aliases_path]:
        if path and os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    item = line.strip().lower()
                    if item and not item.startswith("#"):
                        heldout.add(item)
    return heldout

def clean_text(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def build_term_trie(terms: Set[str]):
    trie = {}
    for term in terms:
        term_tokens = re.findall(r"\b\w+\b", term.lower())
        if not term_tokens:
            continue
        node = trie
        for token in term_tokens:
            node = node.setdefault(token, {})
        node.setdefault(None, set()).add(term)
    return trie

def match_trie(text: str, trie) -> Set[str]:
    tokens = re.findall(r"\b\w+\b", text.lower())
    matches = set()
    for start in range(len(tokens)):
        node = trie
        position = start
        while position < len(tokens):
            node = node.get(tokens[position])
            if node is None:
                break
            matches.update(node.get(None, ()))
            position += 1
    return matches

def find_matching_terms(text: str, terms: Set[str]) -> Set[str]:
    return match_trie(text, build_term_trie(terms))

def chunk_text(text: str, chunk_size: int = 200, overlap: int = 30) -> List[str]:
    words = text.split()
    if len(words) <= chunk_size:
        return [text]
    chunks = []
    step = chunk_size - overlap
    for i in range(0, len(words), step):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
        if i + chunk_size >= len(words):
            break
    return chunks

def contains_heldout_word(text: str, heldout_set: Set[str]) -> bool:
    return bool(find_matching_terms(text, heldout_set))

# ================= PASS 1: COLLECT NAMES & UNTAGGED CHUNKS =================
def run_pass1(files: List[int], raw_dir: str, intermediate_out: str, names_out: str, heldout_set: Set[str]):
    os.makedirs(os.path.dirname(intermediate_out), exist_ok=True)
    os.makedirs(os.path.dirname(names_out), exist_ok=True)

    discovered_drugs = set()
    heldout_trie = build_term_trie(heldout_set)
    intermediate_chunks = []
    seen_hashes = set()

    for p in files:
        zip_path = os.path.join(raw_dir, f"drug-label-{p:04d}-of-0013.json.zip")
        if not os.path.exists(zip_path):
            print(f"Warning: {zip_path} not found. Skipping.")
            continue

        with zipfile.ZipFile(zip_path, "r") as zf:
            for member in zf.namelist():
                if not member.endswith(".json"):
                    continue
                with zf.open(member) as jf:
                    data = json.load(jf)
                    for result in data.get("results", []):
                        openfda = result.get("openfda", {})
                        generic_names = [g.lower().strip() for g in openfda.get("generic_name", []) if g]
                        brand_names = [b.lower().strip() for b in openfda.get("brand_name", []) if b]
                        substance_names = [s.lower().strip() for s in openfda.get("substance_name", []) if s]

                        if not generic_names:
                            continue

                        primary_drug = generic_names[0]
                        # Collect all names for unioning
                        for n in generic_names + brand_names + substance_names:
                            if len(n) >= 4:
                                discovered_drugs.add(n)

                        # Primary label exclusion: drop if primary generic is held out
                        if match_trie(primary_drug, heldout_trie):
                            continue

                        set_id = result.get("set_id", "unknown_set")
                        sections = ["drug_interactions", "warnings", "warnings_and_cautions"]

                        for sec in sections:
                            sec_text_list = result.get(sec, [])
                            if not sec_text_list:
                                continue
                            full_sec_text = clean_text(" ".join(sec_text_list))
                            if len(full_sec_text.split()) < 30:
                                continue

                            for passage in chunk_text(full_sec_text, chunk_size=200, overlap=30):
                                h = hashlib.md5(passage.encode("utf-8")).hexdigest()
                                if h in seen_hashes:
                                    continue
                                seen_hashes.add(h)

                                intermediate_chunks.append({
                                    "doc_id": f"openFDA:{set_id}:{sec}",
                                    "primary_drug": primary_drug,
                                    "section": sec,
                                    "text": passage
                                })

    # Write intermediate untagged chunks
    with open(intermediate_out, "w", encoding="utf-8") as f:
        for c in intermediate_chunks:
            f.write(json.dumps(c) + "\n")

    # Write collected names
    with open(names_out, "w", encoding="utf-8") as f:
        json.dump(sorted(list(discovered_drugs)), f, indent=2)

    print(f"Pass 1 finished: {len(intermediate_chunks)} passages saved, {len(discovered_drugs)} distinct drug names collected.")

# ================= PASS 2: TAG & FILTER WITH FROZEN DICTIONARY =================
def run_pass2(intermediate_in: str, prefix: str, drugs_file: str, aliases_file: str, chunks_out: str, triples_out: str, heldout_file: str = "docs/heldout_drugs.txt"):
    with open(drugs_file, "r", encoding="utf-8") as f:
        drug_dict = set(json.load(f))
    heldout_set = load_heldout(heldout_file, aliases_file)
    heldout_trie = build_term_trie(heldout_set)
    drug_trie = build_term_trie(drug_dict)

    os.makedirs(os.path.dirname(chunks_out), exist_ok=True)
    os.makedirs(os.path.dirname(triples_out), exist_ok=True)

    final_chunks = []
    final_triples = []
    chunk_counter = 1

    tag_removals = 0
    text_removals = 0

    with open(intermediate_in, "r", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line)
            text = item["text"]
            primary_drug = item["primary_drug"]
            if match_trie(primary_drug, heldout_trie):
                tag_removals += 1
                continue

            # Tag drugs present in text
            tagged_drugs = sorted(match_trie(text, drug_trie))

            if not tagged_drugs:
                continue

            # Held-out filtering: tags and whole-word text
            if any(match_trie(drug, heldout_trie) for drug in tagged_drugs):
                tag_removals += 1
                continue

            if match_trie(text, heldout_trie):
                text_removals += 1
                continue

            chunk_id = f"{prefix}_{chunk_counter:06d}"
            final_chunks.append({
                "chunk_id": chunk_id,
                "doc_id": item["doc_id"],
                "text": text,
                "source": "openFDA",
                "drugs": tagged_drugs
            })

            # Rule-based triples
            for other_drug in tagged_drugs:
                if other_drug != primary_drug and not match_trie(other_drug, heldout_trie):
                    final_triples.append({
                        "subject": primary_drug,
                        "relation": "interacts_with",
                        "object": other_drug,
                        "chunk_id": chunk_id,
                        "source": "openFDA"
                    })

            chunk_counter += 1

    with open(chunks_out, "w", encoding="utf-8") as f:
        for c in final_chunks:
            f.write(json.dumps(c) + "\n")

    with open(triples_out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["subject", "relation", "object", "chunk_id", "source"])
        writer.writeheader()
        writer.writerows(final_triples)

    print(f"Pass 2 finished for prefix '{prefix}':")
    print(f"  Chunks: {len(final_chunks)} | Triples: {len(final_triples)}")
    print(f"  Held-out tag removals: {tag_removals} | Held-out text removals: {text_removals}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--collect-names", action="store_true")
    parser.add_argument("--tag-intermediate", action="store_true")
    parser.add_argument("--files", nargs="+", type=int)
    parser.add_argument("--raw-dir", default="data/raw/openfda/")
    parser.add_argument("--intermediate-out")
    parser.add_argument("--intermediate-in")
    parser.add_argument("--names-out")
    parser.add_argument("--prefix")
    parser.add_argument("--drugs", default="data/processed/drugs_of.json")
    parser.add_argument("--heldout-aliases", default="docs/heldout_drug_aliases.txt")
    parser.add_argument("--heldout-drugs", default="docs/heldout_drugs.txt")
    parser.add_argument("--chunks-out")
    parser.add_argument("--triples-out")
    args = parser.parse_args()

    heldout_set = load_heldout("docs/heldout_drugs.txt", args.heldout_aliases)

    if args.collect_names:
        run_pass1(args.files, args.raw_dir, args.intermediate_out, args.names_out, heldout_set)
    elif args.tag_intermediate:
        run_pass2(args.intermediate_in, args.prefix, args.drugs, args.heldout_aliases, args.chunks_out, args.triples_out, args.heldout_drugs)

if __name__ == "__main__":
    main()
