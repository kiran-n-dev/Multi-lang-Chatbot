
# rag/ingest.py
import os
from typing import List, Tuple
from io import BytesIO
from rag.utils import chunk_text
from rag.embeddings import embed_texts
from rag.vectorstore_faiss import FaissStore
from config.settings import DATA_DIR, FAISS_DIR, CHUNK_SIZE, CHUNK_OVERLAP

# Parsers
def read_txt(path: str) -> str:
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()

def read_md(path: str) -> str:
    return read_txt(path)

def read_pdf_bytes(b: bytes) -> str:
    from PyPDF2 import PdfReader
    reader = PdfReader(BytesIO(b))
    texts = []
    for page in reader.pages:
        t = page.extract_text() or ""
        texts.append(t)
    return "\n".join(texts)

def read_pdf(path: str) -> str:
    with open(path, "rb") as fh:
        return read_pdf_bytes(fh.read())

def read_docx_bytes(b: bytes) -> str:
    from docx import Document
    bio = BytesIO(b)
    doc = Document(bio)
    return "\n".join([p.text for p in doc.paragraphs])

def read_docx(path: str) -> str:
    with open(path, "rb") as fh:
        return read_docx_bytes(fh.read())

# Load existing documents from DATA_DIR
def load_documents() -> List[Tuple[str, dict]]:
    docs = []
    for root, _, files in os.walk(DATA_DIR):
        for f in files:
            path = os.path.join(root, f)
            low = f.lower()
            try:
                if low.endswith(".txt"):
                    content = read_txt(path)
                elif low.endswith(".md"):
                    content = read_md(path)
                elif low.endswith(".pdf"):
                    content = read_pdf(path)
                elif low.endswith(".docx"):
                    content = read_docx(path)
                else:
                    continue
                docs.append((content, {"source": path}))
            except Exception as e:
                print(f"Failed to parse {path}: {e}")
    return docs

def _index_chunks(chunks: List[str], metas: List[dict]) -> int:
    if not chunks:
        return 0
    vectors = embed_texts(chunks)
    store = FaissStore(dim=len(vectors[0]), persist_dir=FAISS_DIR)
    store.add(vectors, chunks, metas)
    store.save()
    return len(chunks)

# CLI build index from DATA_DIR
def build_index():
    docs = load_documents()
    all_chunks, metas = [], []
    for content, meta in docs:
        cks = chunk_text(content, CHUNK_SIZE, CHUNK_OVERLAP)
        all_chunks.extend(cks)
        metas.extend([meta] * len(cks))
    if not all_chunks:
        print(f"No documents found in {DATA_DIR}. Add files and re-run.")
        return
    _index_chunks(all_chunks, metas)

# UI helper: ingest uploaded Streamlit files
def ingest_uploaded_files(files) -> int:
    """
    Save uploaded files under data/docs/uploads and index them.
    Returns number of chunks indexed.
    """
    upload_dir = os.path.join(DATA_DIR, "uploads")
    os.makedirs(upload_dir, exist_ok=True)

    all_chunks, metas = [], []
    for f in files:
        filename = f.name
        dest = os.path.join(upload_dir, filename)
        # Persist file
        with open(dest, "wb") as out:
            out.write(f.read())
        # Parse
        low = filename.lower()
        try:
            if low.endswith(".txt") or low.endswith(".md"):
                content = read_txt(dest)
            elif low.endswith(".pdf"):
                with open(dest, "rb") as fh:
                    content = read_pdf_bytes(fh.read())
            elif low.endswith(".docx"):
                with open(dest, "rb") as fh:
                    content = read_docx_bytes(fh.read())
            else:
                # Skip unsupported types (UI restricts types already)
                continue
        except Exception as e:
            print(f"Failed to parse uploaded {filename}: {e}")
            continue

        cks = chunk_text(content, CHUNK_SIZE, CHUNK_OVERLAP)
        all_chunks.extend(cks)
        metas.extend([{"source": dest}] * len(cks))

    return _index_chunks(all_chunks, metas)

if __name__ == "__main__":
    build_index()
