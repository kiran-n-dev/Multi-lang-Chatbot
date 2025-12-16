
# api/routes/upload.py
from fastapi import APIRouter, UploadFile
import os
from typing import List
from rag.ingest import ingest_uploaded_files
from rag.embeddings import embed_texts
from storage.vector import VectorStore
from config.settings import FAISS_DIR

router = APIRouter()

@router.post("/upload")
async def upload(files: List[UploadFile]):
    # Save files temporarily and ingest
    temp_files = []
    for f in files:
        data = await f.read()
        path = os.path.join("data/docs/uploads", f.filename)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as out:
            out.write(data)
        # Create a file-like object for ingest_uploaded_files
        from io import BytesIO
        temp_file = BytesIO(data)
        temp_file.name = f.filename
        temp_files.append(temp_file)
    
    indexed = ingest_uploaded_files(temp_files)
    return {"indexed": indexed}
