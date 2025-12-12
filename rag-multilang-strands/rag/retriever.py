
# rag/retriever.py
from typing import List, Tuple
from rag.embeddings import embed_texts
from rag.vectorstore_faiss import FaissStore
from config.settings import FAISS_DIR, TOP_K

def retrieve_context(query: str) -> List[Tuple[str, dict, float]]:
    vec = embed_texts([query])[0]
    store = FaissStore(dim=len(vec), persist_dir=FAISS_DIR)
    return store.search(vec, TOP_K)

def format_context_snippets(results: List[Tuple[str, dict, float]]) -> str:
    blocks = []
    for txt, meta, score in results:
        blocks.append(f"[source: {meta.get('source')}] {txt}")
    return "\n\n".join(blocks)
