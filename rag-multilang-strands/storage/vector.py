
# storage/vector.py
import os, json
from typing import List, Dict, Any
import numpy as np, faiss

class VectorStore:
    def __init__(self, dim: int, persist_dir: str):
        os.makedirs(persist_dir, exist_ok=True)
        self.index_path = os.path.join(persist_dir, "faiss.index")
        self.meta_path  = os.path.join(persist_dir, "meta.json")
        self.dim = dim

        self.blocks: List[Dict[str, Any]] = []

        if os.path.exists(self.index_path):
            # Existing index
            self.index = faiss.read_index(self.index_path)
            # Try to read meta
            if os.path.exists(self.meta_path):
                try:
                    with open(self.meta_path, "r", encoding="utf-8") as f:
                        m = json.load(f)
                    if isinstance(m, dict) and "blocks" in m and isinstance(m["blocks"], list):
                        self.blocks = m["blocks"]
                    else:
                        print("[VectorStore] Warning: meta.json has no 'blocks'. Starting with empty blocks.")
                except Exception as e:
                    print(f"[VectorStore] Warning: failed to read meta.json: {e}. Starting with empty blocks.")
            else:
                print("[VectorStore] Warning: meta.json missing. Starting with empty blocks.")
        else:
            # New index
            self.index = faiss.IndexFlatIP(self.dim)
            self.blocks = []

    def add(self, vectors: List[List[float]], blocks: List[Dict[str, Any]]):
        if not vectors:
            # nothing to add
            return
        arr = np.array(vectors, dtype="float32")
        self.index.add(arr)
        self.blocks.extend(blocks)

    def save(self):
        faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump({"blocks": self.blocks}, f, ensure_ascii=False)

    def search(self, query_vec: List[float], top_k: int) -> List[Dict[str, Any]]:
        if self.index.ntotal == 0:
            return []
        q = np.array([query_vec], dtype="float32")
        # cap top_k to number of vectors
        k = min(top_k, self.index.ntotal)
        scores, idxs = self.index.search(q, k)
        out = []
        for i, s in zip(idxs[0], scores[0]):
            if i == -1:
                continue
            # Guard against meta length mismatch
            b = dict(self.blocks[i]) if i < len(self.blocks) else {}
            b["score"] = float(s)
            out.append(b)
