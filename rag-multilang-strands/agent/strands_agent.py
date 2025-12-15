
# agent/strands_agent.py

from config.settings import LLM_MODEL_ID
from config.bedrock_client import bedrock_runtime, translate_client
from rag.retriever import retrieve_context, format_context_snippets
from nlp.language import detect_lang
from nlp.prompts import SYSTEM_PROMPT, build_rag_prompt
import json
from api.response_parser import parse_response_for_rendering


# Default handoff message (in English); will be translated per user language when returned early
HANDOFF_MESSAGE = "We are connecting you to our human agent who can assist you further. Please stay tuned."


def _translate_handoff(msg: str, target_lang: str) -> str:
    """Translate the handoff message to the user's language via AWS Translate; fallback to original on error."""
    try:
        client = translate_client()
        resp = client.translate_text(Text=msg, SourceLanguageCode="en", TargetLanguageCode=target_lang)
        return resp.get("TranslatedText", msg)
    except Exception:
        return msg


def answer(user_message: str) -> str:
    """
    Main entry: retrieve context, apply confidence gate, build strict RAG prompt, and call Bedrock.

    MULTILINGUAL SUPPORT:
    - Detects user's language
    - Retrieves context (queries are auto-translated to English for consistent embedding space)
    - Returns answer in user's language
    - Falls back to human handoff if confidence is low

    Returns either the model answer (string) or a translated HANDOFF_MESSAGE when retrieval confidence is low.
    """
    user_lang = detect_lang(user_message)
    print(f"[DEBUG] User query language: {user_lang}")
    print(f"[DEBUG] User message: {user_message}")

    # 1) Retrieve raw results (text, metadata, score)
    # NOTE: retriever.py will auto-translate non-English queries to English before embedding
    results = retrieve_context(user_message)
    
    if not results:
        print(f"[DEBUG] No results retrieved, returning handoff message in {user_lang}")
        return _translate_handoff(HANDOFF_MESSAGE, user_lang)

    # 2) Compute simple confidence metric (max score of returned results)
    try:
        max_score = max([s for (_, _, s) in results if isinstance(s, (int, float))])
    except Exception:
        max_score = 0.0
    
    print(f"[DEBUG] Retrieval confidence score: {max_score:.4f} (threshold: 0.5)")

    # 3) Confidence gate: if too low, escalate to human (prevent hallucination)
    if max_score < 0.5:
        print(f"[DEBUG] Confidence too low ({max_score:.4f} < 0.5), returning handoff in {user_lang}")
        return _translate_handoff(HANDOFF_MESSAGE, user_lang)

    print(f"[DEBUG] Confidence sufficient, generating response in {user_lang}")

    # 4) Format context for prompt builder (this will translate snippets to user_lang as needed)
    context = format_context_snippets(results, user_lang)
    context["confidence_score"] = max_score

    # 5) Build strict RAG prompt
    prompt = build_rag_prompt(user_query=user_message, context=context, handoff_message=HANDOFF_MESSAGE)

    # 6) Call Bedrock converse with a strict temperature=0
    client = bedrock_runtime()
    system = [{"text": SYSTEM_PROMPT}]
    user_content = [{"text": prompt}]
    messages = [{"role": "user", "content": user_content}]

    resp = client.converse(
        modelId=LLM_MODEL_ID,
        system=system,
        messages=messages,
        inferenceConfig={"temperature": 0}
    )

    try:
        txt = resp["output"]["message"]["content"][0]["text"]
    except Exception as e:
        print(f"[DEBUG] Error getting response from Bedrock: {e}")
        return _translate_handoff(HANDOFF_MESSAGE, user_lang)

    # If the model returns the HANDOFF_MESSAGE exactly, translate it and return
    if txt.strip() == HANDOFF_MESSAGE:
        print(f"[DEBUG] Model returned handoff message, translating to {user_lang}")
        return _translate_handoff(HANDOFF_MESSAGE, user_lang)

    # Otherwise return the raw text
    print(f"[DEBUG] Successfully generated response in {user_lang}")
    return txt


def answer_with_converse(user_query: str, user_lang: str = "en") -> dict:
    """
    Compatibility wrapper used by the FastAPI route. Calls `answer()` to get the
    raw model response and parses it into structured components:
      - `text`: combined text blocks
      - `tables`: list of sanitized HTML tables
      - `images`: list of image paths (not implemented here)

    This keeps the API route working while preserving the improved parsing logic.
    """
    raw = answer(user_query)

    # If answer returned a handoff message (string), keep as text
    if not raw:
        return {"text": "", "tables": [], "images": []}

    blocks = parse_response_for_rendering(raw)
    aggregated_text_parts = []
    tables = []
    images = []

    for block in blocks:
        # block may be ('text', content) or ('table', html)
        if block[0] == 'table':
            tables.append(block[1])
        else:
            aggregated_text_parts.append(block[1])

    text = "\n\n".join(aggregated_text_parts).strip()

    return {"text": text, "tables": tables, "images": images}
