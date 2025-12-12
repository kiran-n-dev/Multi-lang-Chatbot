import os
import faiss
import numpy as np
import json
from typing import List, Tuple

class FaissStore:
    def __init__(self, dim: int, persist_dir: str):
        self.dim = dim
        self.persist_dir = persist_dir
        os.makedirs(self.persist_dir, exist_ok=True)
        self.index_path = os.path.join(self.persist_dir, "faiss.index")
        self.meta_path = os.path.join(self.persist_dir, "meta.json")

        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            self.texts = meta["texts"]
            self.metadatas = meta["metadatas"]
        else:
            self.index = faiss.IndexFlatIP(self.dim)
            self.texts = []
            self.metadatas = []

    def add(self, vectors: List[List[float]], texts: List[str], metadatas: List[dict]):
        arr = np.array(vectors, dtype="float32")
        self.index.add(arr)
        self.texts.extend(texts)
        self.metadatas.extend(metadatas)

    def save(self):
        faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump({"texts": self.texts, "metadatas": self.metadatas}, f, ensure_ascii=False)

    def search(self, query_vec: List[float], top_k: int) -> List[Tuple[str, dict, float]]:
        q = np.array([query_vec], dtype="float32")
        scores, idxs = self.index.search(q, top_k)
        results = []
        for i, s in zip(idxs[0], scores[0]):
            if i == -1:
                continue
            results.append((self.texts[i], self.metadatas[i], float(s)))
        return results
