import os

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# Choose your LLM model (ensure access in Bedrock for your region)
LLM_MODEL_ID = os.getenv("LLM_MODEL_ID", "anthropic.claude-3-5-sonnet-20240620-v1:0")

# Embedding model (Titan v2)
EMBEDDING_MODEL_ID = os.getenv("EMBEDDING_MODEL_ID", "amazon.titan-embed-text-v2:0")

DATA_DIR = os.getenv("DATA_DIR", "data/docs")
FAISS_DIR = os.getenv("FAISS_DIR", "storage/faiss_index")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))
TOP_K = int(os.getenv("TOP_K", "4"))
