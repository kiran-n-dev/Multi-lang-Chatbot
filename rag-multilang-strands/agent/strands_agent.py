
# agent/strands_agent.py

from strands import Agent, tool
from config.settings import LLM_MODEL_ID
from rag.retriever import retrieve_context, format_context_snippets
from nlp.language import detect_lang
from nlp.prompts import build_rag_prompt

@tool
def search_knowledge_base(query: str) -> str:
    """Retrieve top-k context snippets relevant to the query from the vector store."""
    results = retrieve_context(query)
    return format_context_snippets(results)

def build_agent() -> Agent:
    agent = Agent(model=LLM_MODEL_ID, tools=[search_knowledge_base])
    return agent

def _extract_text_from_result(result) -> str:
    """
    Try multiple shapes that AgentResult may expose across Strands versions.
    Fallback to last message or string(result) if needed.
    """
    # Common single-attr cases
    for attr in ("output", "text", "content", "final_text"):
        if hasattr(result, attr):
            val = getattr(result, attr)
            if isinstance(val, str):
                return val
            # Some versions store dicts or small objects
            try:
                return val.get("content", str(val))
            except Exception:
                return str(val)

    # Messages-based shape
    if hasattr(result, "messages"):
        msgs = getattr(result, "messages", None)
        if isinstance(msgs, list) and msgs:
            last = msgs[-1]
            # Try message fields
            for attr in ("content", "text", "message", "output"):
                if hasattr(last, attr):
                    v = getattr(last, attr)
                    return v if isinstance(v, str) else str(v)
            # Fallback
            return str(last)

    # Absolute fallback
    return str(result)

def answer(agent: Agent, user_message: str) -> str:
    user_lang = detect_lang(user_message)
    context = search_knowledge_base(user_message)
    prompt = build_rag_prompt(user_message, context, user_lang)
    result = agent(prompt)
    return _extract_text_from_result(result)
