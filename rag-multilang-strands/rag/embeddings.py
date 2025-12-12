import json
from typing import List
from config.bedrock_client import bedrock_runtime
from config.settings import EMBEDDING_MODEL_ID

DEFAULT_DIM = 1024

def embed_texts(texts: List[str], normalize: bool = True, dimensions: int = DEFAULT_DIM) -> List[List[float]]:
    client = bedrock_runtime()
    embeddings = []
    for t in texts:
        body = json.dumps({"inputText": t, "dimensions": dimensions, "normalize": normalize})
        resp = client.invoke_model(modelId=EMBEDDING_MODEL_ID, body=body, accept="application/json", contentType="application/json")
        payload = json.loads(resp.get("body").read())
        embeddings.append(payload["embedding"])
    return embeddings
