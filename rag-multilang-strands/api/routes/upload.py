
# api/routes/upload.py
from fastapi import APIRouter, UploadFile
import os
from typing import List
from rag.ingest import ingest_file
from rag.embeddings import embed_texts
from storage.vector import VectorStore
from config.settings import FAISS_DIR

router = APIRouter()

@router.post("/upload")
async def upload(files: List[UploadFile]):
    all_blocks = []
    for f in files:
        data = await f.read()
        path = os.path.join("data/docs/uploads", f.filename)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as out:
            out.write(data)
        blocks = ingest_file(path)
        all_blocks.extend(blocks)

    texts = [b["plain_text"] for b in all_blocks if "plain_text" in b]
    if not texts:
        return {"indexed": 0}

    vecs = embed_texts(texts)

    store = VectorStore(dim=len(vecs[0]), persist_dir=FAISS_DIR)
    text_blocks = [b for b in all_blocks if "plain_text" in b]
    store.add(vecs, text_blocks)
    store.save()

    return {"indexed": len(texts)}
