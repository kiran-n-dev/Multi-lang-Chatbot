# Multi-language RAG Chatbot (Strands + AWS Bedrock)

Quick start:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt

# Put your .txt/.md docs into data/docs
python -m rag.ingest
streamlit run app.py
```

Configure model IDs and region in `config/settings.py` or environment variables.
