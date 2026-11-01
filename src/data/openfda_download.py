import argparse
import hashlib
import json
import os
import urllib.request
from typing import List

OPENFDA_BASE_URL = "https://download.open.fda.gov/drug/label/"

def compute_sha256(filepath: str) -> str:
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

def download_partition(partition_num: int, out_dir: str):
    os.makedirs(out_dir, exist_ok=True)
    filename = f"drug-label-{partition_num:04d}-of-0013.json.zip"
    url = f"{OPENFDA_BASE_URL}{filename}"
    target_path = os.path.join(out_dir, filename)

    if os.path.exists(target_path):
        print(f"[{filename}] Already exists. Skipping download.")
    else:
        print(f"Downloading {url} ...")
        try:
            urllib.request.urlretrieve(url, target_path)
            print(f"Downloaded {filename}.")
        except Exception as e:
            print(f"Failed to download {filename}: {e}")
            return

    size_bytes = os.path.getsize(target_path)
    sha256_hash = compute_sha256(target_path)
    print(f"File: {filename} | Bytes: {size_bytes} | SHA-256: {sha256_hash}")

def main():
    parser = argparse.ArgumentParser(description="Download openFDA partition files.")
    parser.add_argument("--files", nargs="+", type=int, required=True, help="Partition indices (e.g., 1 2 3 4 5 6 7 8 9)")
    parser.add_argument("--out-dir", type=str, default="data/raw/openfda/", help="Directory to save raw ZIPs")
    args = parser.parse_args()

    for p in args.files:
        download_partition(p, args.out_dir)

if __name__ == "__main__":
    main()
