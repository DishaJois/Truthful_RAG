
import argparse
import csv
import hashlib
import json
import os
import re
import zipfile
from typing import Dict, List, Set, Any


# ================= COMMON HELPERS =================

def normalize_drug_text(text: str) -> str:
    """
    Convert drug names and text into a consistent format.

    Example:
        Amoxicillin-Clavulanate -> amoxicillin clavulanate
        Sodium   Chloride       -> sodium chloride
    """
    text = text.lower()
    text = re.sub(r"[^\w]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def load_heldout(heldout_path: str, aliases_path: str) -> Set[str]:
    """
    Load canonical held-out drug names and their aliases.
    Ignore blank lines and comments beginning with #.
    """
    heldout = set()

    for path in [heldout_path, aliases_path]:
        if path and os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    item = line.strip()

                    if item and not item.startswith("#"):
                        normalized = normalize_drug_text(item)

                        if normalized:
                            heldout.add(normalized)

    return heldout


def build_drug_matcher(drug_dict: Set[str]) -> Dict[str, Any]:
    """
    Build a token trie for efficient multi-word drug matching.

    The trie is built once and reused for all passages.
    """
    root = {}

    for drug in drug_dict:
        normalized = normalize_drug_text(drug)

        if not normalized:
            continue

        tokens = normalized.split()
        node = root

        for token in tokens:
            if token not in node:
                node[token] = {}

            node = node[token]

        # None marks the end of a complete drug name.
        node.setdefault(None, []).append(drug)

    return root


def find_drug_matches(text: str, matcher: Dict[str, Any]) -> List[str]:
    """
    Find complete drug-name phrases in text using the trie.

    Supports single-word and multi-word drug names.
    Avoids matching partial words.
    """
    tokens = normalize_drug_text(text).split()
    matches = set()

    for start in range(len(tokens)):
        node = matcher

        for token in tokens[start:]:
            if token not in node:
                break

            node = node[token]

            if None in node:
                matches.update(node[None])

    return sorted(matches)


def contains_heldout_word(
    text: str,
    heldout_matcher: Dict[str, Any]
) -> bool:
    """
    Check whether text contains any complete held-out drug name or alias.
    """
    return bool(find_drug_matches(text, heldout_matcher))


def clean_text(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def chunk_text(
    text: str,
    chunk_size: int = 200,
    overlap: int = 30
) -> List[str]:

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


def create_parent_directory(path: str):
    """Create the parent directory only when one is specified."""
    parent = os.path.dirname(path)

    if parent:
        os.makedirs(parent, exist_ok=True)


# ================= PASS 1: COLLECT NAMES & UNTAGGED CHUNKS =================

def run_pass1(
    files: List[int],
    raw_dir: str,
    intermediate_out: str,
    names_out: str,
    heldout_set: Set[str]
):

    create_parent_directory(intermediate_out)
    create_parent_directory(names_out)

    discovered_drugs = set()
    intermediate_chunks = []
    seen_hashes = set()

    # Normalize held-out names before comparing primary drug names.
    normalized_heldout = {
        normalize_drug_text(name)
        for name in heldout_set
    }

    for p in files:

        zip_path = os.path.join(
            raw_dir,
            f"drug-label-{p:04d}-of-0013.json.zip"
        )

        if not os.path.exists(zip_path):
            print(f"Warning: {zip_path} not found. Skipping.")
            continue

        print(f"Processing OpenFDA partition {p}...")

        with zipfile.ZipFile(zip_path, "r") as zf:

            for member in zf.namelist():

                if not member.endswith(".json"):
                    continue

                with zf.open(member) as jf:

                    data = json.load(jf)

                    for result in data.get("results", []):

                        openfda = result.get("openfda", {})

                        generic_names = [
                            g.lower().strip()
                            for g in openfda.get("generic_name", [])
                            if g
                        ]

                        brand_names = [
                            b.lower().strip()
                            for b in openfda.get("brand_name", [])
                            if b
                        ]

                        substance_names = [
                            s.lower().strip()
                            for s in openfda.get("substance_name", [])
                            if s
                        ]

                        if not generic_names:
                            continue

                        primary_drug = generic_names[0]

                        # Collect all names for team dictionary union.
                        for name in (
                            generic_names + brand_names + substance_names
                        ):
                            if len(name) >= 4:
                                discovered_drugs.add(name)

                        # Exclude held-out primary drugs.
                        if normalize_drug_text(primary_drug) in normalized_heldout:
                            continue

                        set_id = result.get("set_id", "unknown_set")

                        sections = [
                            "drug_interactions",
                            "warnings",
                            "warnings_and_cautions"
                        ]

                        for sec in sections:

                            sec_text_list = result.get(sec, [])

                            if not sec_text_list:
                                continue

                            full_sec_text = clean_text(
                                " ".join(sec_text_list)
                            )

                            if len(full_sec_text.split()) < 30:
                                continue

                            for passage in chunk_text(
                                full_sec_text,
                                chunk_size=200,
                                overlap=30
                            ):

                                h = hashlib.md5(
                                    passage.encode("utf-8")
                                ).hexdigest()

                                if h in seen_hashes:
                                    continue

                                seen_hashes.add(h)

                                intermediate_chunks.append({
                                    "doc_id": f"openFDA:{set_id}:{sec}",
                                    "primary_drug": primary_drug,
                                    "section": sec,
                                    "text": passage
                                })

    # Save intermediate passages.
    with open(intermediate_out, "w", encoding="utf-8") as f:

        for chunk in intermediate_chunks:
            f.write(json.dumps(chunk) + "\n")

    # Save discovered drug names.
    with open(names_out, "w", encoding="utf-8") as f:

        json.dump(
            sorted(list(discovered_drugs)),
            f,
            indent=2
        )

    print("\nPass 1 finished:")
    print(f"  Passages saved: {len(intermediate_chunks)}")
    print(f"  Distinct drug names: {len(discovered_drugs)}")


# ================= PASS 2: TAG & FILTER WITH FROZEN DICTIONARY =================

def run_pass2(
    intermediate_in: str,
    prefix: str,
    drugs_file: str,
    heldout_file: str,
    aliases_file: str,
    chunks_out: str,
    triples_out: str
):

    # Load frozen team drug dictionary.
    with open(drugs_file, "r", encoding="utf-8") as f:
        drug_dict = {
            drug.strip().lower()
            for drug in json.load(f)
            if drug and drug.strip()
        }

    # Load canonical held-out names AND aliases.
    heldout_set = load_heldout(
        heldout_file,
        aliases_file
    )

    print(f"Loaded drug dictionary: {len(drug_dict)} names")
    print(f"Loaded held-out names and aliases: {len(heldout_set)}")

    # Build both matchers only once.
    print("Building drug matcher...")
    drug_matcher = build_drug_matcher(drug_dict)

    print("Building held-out matcher...")
    heldout_matcher = build_drug_matcher(heldout_set)

    create_parent_directory(chunks_out)
    create_parent_directory(triples_out)

    final_chunks = []
    final_triples = []

    chunk_counter = 1

    tag_removals = 0
    text_removals = 0
    unmatched_passages = 0

    with open(intermediate_in, "r", encoding="utf-8") as f:

        for line in f:

            item = json.loads(line)

            text = item["text"]
            primary_drug = item["primary_drug"]

            # Find single-word and multi-word drug names.
            tagged_drugs = find_drug_matches(
                text,
                drug_matcher
            )

            if not tagged_drugs:
                unmatched_passages += 1
                continue

            # Remove passages containing held-out drug tags.
            if any(
                normalize_drug_text(drug) in heldout_set
                for drug in tagged_drugs
            ):
                tag_removals += 1
                continue

            # Remove passages containing held-out names or aliases.
            if contains_heldout_word(text, heldout_matcher):
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

            # Generate rule-based interaction triples.
            normalized_primary = normalize_drug_text(primary_drug)

            for other_drug in tagged_drugs:

                normalized_other = normalize_drug_text(other_drug)

                if (
                    normalized_other != normalized_primary
                    and normalized_other not in heldout_set
                ):

                    final_triples.append({
                        "subject": primary_drug,
                        "relation": "interacts_with",
                        "object": other_drug,
                        "chunk_id": chunk_id,
                        "source": "openFDA"
                    })

            chunk_counter += 1

    # Save final chunks.
    with open(chunks_out, "w", encoding="utf-8") as f:

        for chunk in final_chunks:
            f.write(json.dumps(chunk) + "\n")

    # Save triples.
    with open(triples_out, "w", newline="", encoding="utf-8") as f:

        writer = csv.DictWriter(
            f,
            fieldnames=[
                "subject",
                "relation",
                "object",
                "chunk_id",
                "source"
            ]
        )

        writer.writeheader()
        writer.writerows(final_triples)

    print(f"\nPass 2 finished for prefix '{prefix}':")
    print(f"  Chunks: {len(final_chunks)}")
    print(f"  Triples: {len(final_triples)}")
    print(f"  Held-out tag removals: {tag_removals}")
    print(f"  Held-out text removals: {text_removals}")
    print(f"  Unmatched passages: {unmatched_passages}")


# ================= MAIN =================

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--collect-names", action="store_true")
    parser.add_argument("--tag-intermediate", action="store_true")

    parser.add_argument("--files", nargs="+", type=int)

    parser.add_argument(
        "--raw-dir",
        default="data/raw/openfda/"
    )

    parser.add_argument("--intermediate-out")
    parser.add_argument("--intermediate-in")
    parser.add_argument("--names-out")
    parser.add_argument("--prefix")

    parser.add_argument(
        "--drugs",
        default="data/processed/drugs_of.json"
    )

    parser.add_argument(
        "--heldout",
        default="docs/heldout_drugs.txt"
    )

    parser.add_argument(
        "--heldout-aliases",
        default="docs/heldout_drug_aliases.txt"
    )

    parser.add_argument("--chunks-out")
    parser.add_argument("--triples-out")

    args = parser.parse_args()

    if args.collect_names:

        if not args.files or not args.intermediate_out or not args.names_out:
            parser.error(
                "--collect-names requires --files, "
                "--intermediate-out and --names-out"
            )

        heldout_set = load_heldout(
            args.heldout,
            args.heldout_aliases
        )

        run_pass1(
            args.files,
            args.raw_dir,
            args.intermediate_out,
            args.names_out,
            heldout_set
        )

    elif args.tag_intermediate:

        required = [
            args.intermediate_in,
            args.prefix,
            args.chunks_out,
            args.triples_out
        ]

        if not all(required):
            parser.error(
                "--tag-intermediate requires --intermediate-in, "
                "--prefix, --chunks-out and --triples-out"
            )

        run_pass2(
            args.intermediate_in,
            args.prefix,
            args.drugs,
            args.heldout,
            args.heldout_aliases,
            args.chunks_out,
            args.triples_out
        )

    else:
        parser.error(
            "Specify either --collect-names or --tag-intermediate"
        )


if __name__ == "__main__":
    main()
