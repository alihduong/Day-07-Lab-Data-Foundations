from __future__ import annotations

import hashlib
import math

LOCAL_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_PROVIDER_ENV = "EMBEDDING_PROVIDER"


class MockEmbedder:
    """Deterministic embedding backend used by tests and default classroom runs."""

    def __init__(self, dim: int = 64) -> None:
        self.dim = dim
        self._backend_name = "mock embeddings fallback"

    def __call__(self, text: str) -> list[float]:
        digest = hashlib.md5(text.encode()).hexdigest()
        seed = int(digest, 16)
        vector = []
        for _ in range(self.dim):
            seed = (seed * 1664525 + 1013904223) & 0xFFFFFFFF
            vector.append((seed / 0xFFFFFFFF) * 2 - 1)
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]


class LocalEmbedder:
    """Sentence Transformers-backed local embedder."""

    def __init__(self, model_name: str = LOCAL_EMBEDDING_MODEL) -> None:
        self.model_name = model_name
        # Default to mock until proven we can load a real model
        self._backend_name = "mock embeddings fallback"
        self._mock = MockEmbedder()
        self.model = None
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore

            self.model = SentenceTransformer(model_name)
            self._backend_name = model_name
            self._mock = None  # type: ignore
        except Exception:
            # Any import/load error (e.g., missing torch/transformers) → graceful fallback
            # Keep self.model = None and use mock backend
            pass

    def __call__(self, text: str) -> list[float]:
        if self.model is None:
            # Fallback path
            return self._mock(text)  # type: ignore[arg-type]
        embedding = self.model.encode(text, normalize_embeddings=True)
        if hasattr(embedding, "tolist"):
            return embedding.tolist()
        return [float(value) for value in embedding]


class OpenAIEmbedder:
    """OpenAI embeddings API-backed embedder."""

    def __init__(self, model_name: str = OPENAI_EMBEDDING_MODEL) -> None:
        self.model_name = model_name
        # Default to mock until a real client is created
        self._backend_name = "mock embeddings fallback"
        self._mock = MockEmbedder()
        self.client = None
        try:
            from openai import OpenAI  # type: ignore

            self.client = OpenAI()
            self._backend_name = model_name
            self._mock = None  # type: ignore
        except Exception:
            # Missing SDK or auth → graceful fallback
            pass

    def __call__(self, text: str) -> list[float]:
        if self.client is None:
            return self._mock(text)  # type: ignore[arg-type]
        response = self.client.embeddings.create(model=self.model_name, input=text)
        return [float(value) for value in response.data[0].embedding]


_mock_embed = MockEmbedder()
