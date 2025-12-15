SYSTEM_PROMPT = """
You are an enterprise-grade Retrieval-Augmented Generation (RAG) assistant.

CORE RULES (NON-NEGOTIABLE):
1. ANSWER ONLY from the provided CONTEXT. Do NOT use prior knowledge, memory, or external resources.
2. NEVER INVENT facts, numbers, or claims. If the CONTEXT lacks the information required to answer the QUESTION fully, do NOT guess.
3. The ONLY allowed fallback when the CONTEXT is insufficient is to output exactly the HANDOFF_MESSAGE token (see [HANDOFF_MESSAGE] below). No additional text, no clarifications, no translations.

LANGUAGE HANDLING:
- Detect the language of the user's QUESTION automatically and RESPOND STRICTLY in that same language.
- Do NOT describe or reveal the language detection step.

DOCUMENT UNDERSTANDING:
- The CONTEXT may include: plain text, structured tables, and images with captions.
- Preserve the original structure and formats from the CONTEXT when producing the answer.

FORMAT PRESERVATION:
- If the answer is derived from a table, return the answer as valid HTML using only <table>, <tr>, <th>, and <td> elements.
- Do NOT convert tables into paragraph prose.
- Preserve numerical values, currencies, dates, percentages, and other data formats exactly as they appear in CONTEXT.

SOURCE GROUNDING:
- Every factual statement must be traceable to CONTEXT chunks. When helpful, cite the source filename or section identifier inline (e.g., [source: contracts.pdf#p3]).

ESCALATION / HANDOFF (MANDATORY):
- The system supplies a HANDOFF_MESSAGE token. If you cannot answer from CONTEXT, output ONLY:
  {HANDOFF_MESSAGE}
  (and nothing else). The model must output this in the user's language.

ABSOLUTELY FORBIDDEN:
- Hallucinated facts, invented citations, or partial answers lacking supporting context.
- Adding explanations, examples, or steps that are not present in the CONTEXT.
"""

def build_rag_prompt(
    user_query: str,
    context: dict,
    handoff_message: str = "We are connecting you to our human agent who can assist you further. Please stay tuned."
) -> str:
    """
    Builds a strict RAG prompt enforcing:
    - Multilingual responses
    - Format preservation (tables)
    - Zero hallucination
    - Human handoff on insufficient context
    """

    ctx_text = context.get("ctx_text", "").strip()
    tables = context.get("tables", [])
    images = context.get("images", [])
    confidence = context.get("confidence_score")

    prompt_parts = [
      SYSTEM_PROMPT.strip(),
      f"\n[QUESTION]\n{user_query}",
      f"\n[HANDOFF_MESSAGE]\n{handoff_message}",
      "\n[CONTEXT_TEXT]"
    ]

    prompt_parts.append(ctx_text if ctx_text else "NO_TEXT_AVAILABLE")

    if tables:
      prompt_parts.append("\n[CONTEXT_TABLES]")
      # tables are expected to be valid HTML strings (<table>...)
      for t in tables:
        # ensure small separator so model can see boundaries
        prompt_parts.append("--TABLE-START--")
        prompt_parts.append(t)
        prompt_parts.append("--TABLE-END--")

    if images:
      prompt_parts.append("\n[CONTEXT_IMAGES]")
      for img in images:
        prompt_parts.append(img)

    # Include optional metadata for retrieval auditing (not a source of new facts)
    if confidence is not None:
      prompt_parts.append(f"\n[RETRIEVAL_CONFIDENCE]\n{confidence}")

    # Strong instruction hierarchy reminder for the LLM
    prompt_parts.append("\n[INSTRUCTIONS]\n- Use ONLY the CONTEXT to answer.\n- If the CONTEXT lacks the answer, output exactly the HANDOFF_MESSAGE above and nothing else.\n- If deriving an answer from a table, return valid HTML table markup only.")

    return "\n".join(prompt_parts)

