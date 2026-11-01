import json
import os
import numpy as np

try:
    import faiss
    from sentence_transformers import SentenceTransformer
except ImportError:
    pass

def build_faiss_index(
    merged_chunks_path: str = "data/processed/chunks.jsonl",
    index_out: str = "data/processed/faiss.index",
    ids_out: str = "data/processed/chunk_ids.json",
    model_name: str = "all-MiniLM-L6-v2",
    shard_size: int = 10000
):
    print(f"Loading embedding model: {model_name}...")
    model = SentenceTransformer(model_name)

    chunk_ids = []
    texts = []

    print(f"Reading merged chunks from {merged_chunks_path}...")
    with open(merged_chunks_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            item = json.loads(line)
            chunk_ids.append(item["chunk_id"])
            texts.append(item["text"])

    total = len(texts)
    print(f"Total passages to encode: {total}")

    embeddings = []
    for i in range(0, total, shard_size):
        batch_texts = texts[i:i + shard_size]
        print(f"Encoding shard {i // shard_size + 1} ({i} to {min(i + shard_size, total)})...")
        emb_batch = model.encode(batch_texts, show_progress_bar=True, normalize_embeddings=True)
        embeddings.append(emb_batch)

    all_embs = np.vstack(embeddings).astype("float32")
    dim = all_embs.shape[1]

    print(f"Building FAISS IndexFlatIP (dimension={dim}, vectors={all_embs.shape[0]})...")
    index = faiss.IndexFlatIP(dim)
    index.add(all_embs)

    # Strict playbook alignment assertions
    assert index.ntotal == len(chunk_ids), "Vector count does not match chunk ID count!"
    assert len(chunk_ids) == total, "Chunk ID count does not match original chunk count!"

    os.makedirs(os.path.dirname(index_out), exist_ok=True)
    faiss.write_index(index, index_out)

    with open(ids_out, "w", encoding="utf-8") as f:
        json.dump(chunk_ids, f)

    print(f"Index successfully written to {index_out}")
    print(f"Chunk ID mapping written to {ids_out}")

if __name__ == "__main__":
    build_faiss_index()
