
# rag/retriever.py
from typing import List, Tuple
import re
from rag.embeddings import embed_texts
from rag.vectorstore_faiss import FaissStore
from config.bedrock_client import translate_client
from config.settings import FAISS_DIR, TOP_K
from nlp.language import detect_lang

def translate_query_to_english(query: str) -> str:
    """
    Translate a non-English query to English for consistent embedding space retrieval.
    
    This is critical for multilingual RAG: the embedding model generates different vector spaces
    for different languages. Since all indexed documents are in their source language (mostly English),
    we must translate non-English queries to English BEFORE embedding to ensure they land in the same
    vector space as the documents.
    
    Args:
        query: The user's query (potentially non-English)
        
    Returns:
        Query translated to English (or original if already English)
    """
    query_lang = detect_lang(query)
    
    # If already English, return as-is
    if query_lang == "en":
        return query
    
    # Translate to English for consistent retrieval
    try:
        client = translate_client()
        response = client.translate_text(
            Text=query,
            SourceLanguageCode=query_lang,
            TargetLanguageCode="en"
        )
        translated = response.get("TranslatedText", query)
        print(f"[DEBUG] Translated query from {query_lang}: '{query}' → '{translated}'")
        return translated
    except Exception as e:
        print(f"[WARNING] Query translation failed ({query_lang}): {e}. Using original query.")
        return query

def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    if source_lang == target_lang:
        return text
    # Preserve financial data: numbers, currencies
    # Split text into translatable and non-translatable parts
    parts = re.split(r'(\d+(?:\.\d+)?|\$\d+(?:\.\d+)?|\d+\$)', text)
    translated_parts = []
    client = translate_client()
    try:
        for part in parts:
            if re.match(r'\d+(?:\.\d+)?|\$\d+(?:\.\d+)?|\d+\$', part):
                # Keep as is
                translated_parts.append(part)
            else:
                if part.strip():
                    response = client.translate_text(
                        Text=part,
                        SourceLanguageCode=source_lang,
                        TargetLanguageCode=target_lang
                    )
                    translated_parts.append(response["TranslatedText"])
                else:
                    translated_parts.append(part)
        return ''.join(translated_parts)
    except Exception as e:
        print(f"Translation failed: {e}")
        return text  # Fallback to original

def retrieve_context(query: str) -> List[Tuple[str, dict, float]]:
    """
    Retrieve relevant context chunks for the user's query.
    
    CRITICAL: Translates non-English queries to English BEFORE embedding.
    This ensures queries land in the same embedding vector space as documents,
    solving the multilingual retrieval problem.
    
    Args:
        query: User's query (can be any language)
        
    Returns:
        List of (text, metadata, similarity_score) tuples
    """
    # Step 1: Translate query to English if needed (CRITICAL for multilingual support)
    english_query = translate_query_to_english(query)
    
    # Step 2: Embed the English query (now in same space as documents)
    vec = embed_texts([english_query])[0]
    
    # Step 3: Search FAISS index
    store = FaissStore(dim=len(vec), persist_dir=FAISS_DIR)
    return store.search(vec, TOP_K)

def format_context_snippets(results: List[Tuple[str, dict, float]], user_lang: str) -> str:
    blocks = []
    tables = []
    images = []
    for txt, meta, score in results:
        source_lang = meta.get("lang", "en")
        if txt.strip():  # Only translate non-empty text
            translated_txt = translate_text(txt, source_lang, user_lang)
            blocks.append(f"[source: {meta.get('source')}] {translated_txt}")
        if "table_html" in meta:
            # Translate text inside HTML
            html = meta["table_html"]
            # Simple: translate text between tags, but for now, translate the whole as text then put back? Complicated.
            # For simplicity, translate the plain_text if available, but since table has plain_text, use that.
            if "plain_text" in meta:
                translated_flat = translate_text(meta["plain_text"], source_lang, user_lang)
                # But to keep HTML, perhaps replace text in HTML.
                # For now, include translated flat as context.
                blocks.append(f"[table: {meta.get('source')}] {translated_flat}")
            tables.append(meta["table_html"])  # Keep original HTML for now
        if "image_path" in meta:
            images.append(meta["image_path"])
    context = "\n\n".join(blocks)
    return {"ctx_text": context, "tables": tables, "images": images}
