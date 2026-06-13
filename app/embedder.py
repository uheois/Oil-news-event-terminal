import hashlib
import json
import numpy as np
from config import OPENAI_API_KEY

try:
    from openai import OpenAI
except Exception:
    OpenAI = None


def _fallback_embedding(text: str, dim: int = 384) -> list[float]:
    """Offline deterministic fallback so the MVP runs without an API key."""
    tokens = text.lower().split()
    vec = np.zeros(dim)
    for token in tokens:
        h = int(hashlib.sha256(token.encode()).hexdigest(), 16)
        vec[h % dim] += 1
    norm = np.linalg.norm(vec)
    if norm:
        vec = vec / norm
    return vec.tolist()


def embed_text(text: str) -> list[float]:
    if OPENAI_API_KEY and OpenAI is not None:
        client = OpenAI(api_key=OPENAI_API_KEY)
        res = client.embeddings.create(model="text-embedding-3-small", input=text)
        return res.data[0].embedding
    return _fallback_embedding(text)


def dumps_embedding(vec: list[float]) -> str:
    return json.dumps(vec)


def loads_embedding(s: str) -> list[float]:
    return json.loads(s)
