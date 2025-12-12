SYSTEM_PROMPT = ("You are a helpful multilingual assistant.\n"
                "Always answer in the user\'s language.\n"
                "Ground your answer strictly in the provided CONTEXT. If the context is insufficient, say so.\n"
                "Cite source filenames inline when useful.\n")

def build_rag_prompt(user_query: str, context: str, user_lang: str) -> str:
    return f"{SYSTEM_PROMPT}\n\n[USER_LANGUAGE]: {user_lang}\n[QUESTION]: {user_query}\n\n[CONTEXT]:\n{context}"
