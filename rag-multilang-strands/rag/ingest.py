
# rag/ingest.py
import os
from typing import List, Tuple
from io import BytesIO
from langdetect import detect
from rag.utils import chunk_text
from rag.embeddings import embed_texts
from rag.vectorstore_faiss import FaissStore
from parsers.pdf_parser import parse_pdf_bytes
from parsers.docx_parser import parse_docx_bytes
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
                if low.endswith(".pdf"):
                    with open(path, "rb") as fh:
                        blocks = parse_pdf_bytes(fh.read(), path)
                elif low.endswith(".docx"):
                    with open(path, "rb") as fh:
                        blocks = parse_docx_bytes(fh.read(), path)
                elif low.endswith(".txt"):
                    content = read_txt(path)
                    lang = detect(content) if content.strip() else "en"
                    docs.append((content, {"source": path, "lang": lang}))
                    continue
                elif low.endswith(".md"):
                    content = read_md(path)
                    lang = detect(content) if content.strip() else "en"
                    docs.append((content, {"source": path, "lang": lang}))
                    continue
                else:
                    continue
                
                for block in blocks:
                    if "plain_text" in block and block["plain_text"] is not None:
                        lang = detect(block["plain_text"]) if block["plain_text"].strip() else "en"
                        block["lang"] = lang
                        docs.append((block["plain_text"], block))
                    else:
                        # For tables, etc., add with empty text for now
                        docs.append(("", block))
            except Exception as e:
                print(f"Failed to parse {path}: {e}")
    return docs

def _index_chunks(chunks: List[str], metas: List[dict]) -> int:
    if not chunks:
        return 0
    # Filter out empty chunks to avoid embedding errors
    valid_indices = [i for i, c in enumerate(chunks) if c.strip()]
    if not valid_indices:
        return 0
    valid_chunks = [chunks[i] for i in valid_indices]
    valid_metas = [metas[i] for i in valid_indices]
    vectors = embed_texts(valid_chunks)
    store = FaissStore(dim=len(vectors[0]), persist_dir=FAISS_DIR)
    store.add(vectors, valid_chunks, valid_metas)
    store.save()
    return len(valid_chunks)

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
            if low.endswith(".pdf"):
                with open(dest, "rb") as fh:
                    blocks = parse_pdf_bytes(fh.read(), dest)
            elif low.endswith(".docx"):
                with open(dest, "rb") as fh:
                    blocks = parse_docx_bytes(fh.read(), dest)
            elif low.endswith(".txt"):
                content = read_txt(dest)
                lang = detect(content) if content.strip() else "en"
                cks = chunk_text(content, CHUNK_SIZE, CHUNK_OVERLAP)
                all_chunks.extend(cks)
                metas.extend([{"source": dest, "lang": lang}] * len(cks))
                continue
            elif low.endswith(".md"):
                content = read_md(dest)
                lang = detect(content) if content.strip() else "en"
                cks = chunk_text(content, CHUNK_SIZE, CHUNK_OVERLAP)
                all_chunks.extend(cks)
                metas.extend([{"source": dest, "lang": lang}] * len(cks))
                continue
            else:
                # Skip unsupported types (UI restricts types already)
                continue
            
            for block in blocks:
                if "plain_text" in block and block["plain_text"] is not None:
                    lang = detect(block["plain_text"]) if block["plain_text"].strip() else "en"
                    block["lang"] = lang
                    cks = chunk_text(block["plain_text"], CHUNK_SIZE, CHUNK_OVERLAP)
                    all_chunks.extend(cks)
                    metas.extend([block] * len(cks))
                else:
                    # For tables, store without chunking
                    all_chunks.append("")  # Empty text for embedding
                    metas.append(block)
        except Exception as e:
            print(f"Failed to parse uploaded {filename}: {e}")
            continue

    return _index_chunks(all_chunks, metas)

if __name__ == "__main__":
    build_index()
