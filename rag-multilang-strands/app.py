
# app.py
import streamlit as st
import os
from agent.strands_agent import build_agent, answer
from rag.ingest import ingest_uploaded_files
from nlp.language import detect_lang

st.set_page_config(page_title="Multi‑language RAG Chatbot", page_icon="💬")
st.title("💬 Multi‑language RAG Chatbot (Strands + Bedrock)")

@st.cache_resource
def _agent():
    return build_agent()

# --- Upload section ---
st.header("📄 Upload knowledge files")
st.caption("Supported: .txt, .md, .pdf, .docx")
uploaded = st.file_uploader(
    "Drag & drop or browse",
    type=["txt", "md", "pdf", "docx"], accept_multiple_files=True
)

if uploaded:
    with st.spinner("Indexing uploaded files…"):
        n_chunks = ingest_uploaded_files(uploaded)  # save + chunk + embed + add to FAISS
    st.success(f"Indexed {len(uploaded)} file(s) with ~{n_chunks} chunks.")

st.header("💬 Ask in any language")
if "history" not in st.session_state:
    st.session_state.history = []

for role, content in st.session_state.history:
    with st.chat_message(role):
        st.markdown(content)

prompt = st.chat_input("Type your question in any language…")
if prompt:
    # Show detected language (just for transparency)
    lang = detect_lang(prompt)
    st.toast(f"Detected language: {lang}")

    st.session_state.history.append(("user", prompt))
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            try:
                res = answer(_agent(), prompt)
            except Exception as e:
                res = f"Error: {e}"
        st.markdown(res)
        st.session_state.history.append(("assistant", res))
