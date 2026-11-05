"""Local text embeddings with BAAI/bge-small-en-v1.5 through fastembed."""

from pathlib import Path
from typing import Protocol

import numpy as np
from fastembed import TextEmbedding

MODEL_NAME = "BAAI/bge-small-en-v1.5"
EMBEDDING_DIM = 384

# BGE v1.5 was trained with this instruction in front of search queries (never in
# front of passages). fastembed's query_embed does not add it for this model, so
# this module adds it, exactly once.
BGE_QUERY_PREFIX = "Represent this sentence for searching relevant passages: "


class Embedder(Protocol):
    """Anything that turns text into EMBEDDING_DIM-long vectors. Tests use a fake."""

    def embed_passages(self, texts: list[str]) -> list[np.ndarray]: ...

    def embed_query(self, text: str) -> np.ndarray: ...


class FastEmbedEmbedder:
    """Runs the model locally on CPU. The first use downloads it (about 70 MB) to cache_dir.

    The model is loaded on first use, so an ingest run where every file is
    unchanged never loads it.
    """

    def __init__(self, cache_dir: Path) -> None:
        self._cache_dir = cache_dir
        self._model: TextEmbedding | None = None

    def embed_passages(self, texts: list[str]) -> list[np.ndarray]:
        if self._model is None:
            self._model = TextEmbedding(model_name=MODEL_NAME, cache_dir=str(self._cache_dir))
        return [self._checked(vector) for vector in self._model.embed(texts)]

    def embed_query(self, text: str) -> np.ndarray:
        return self.embed_passages([BGE_QUERY_PREFIX + text])[0]

    @staticmethod
    def _checked(vector: np.ndarray) -> np.ndarray:
        # A different model (or a fastembed change) must fail loudly here,
        # not later as a confusing database error on the vector(384) column.
        if vector.shape != (EMBEDDING_DIM,):
            raise RuntimeError(
                f"{MODEL_NAME} returned a vector of shape {vector.shape}, expected {EMBEDDING_DIM}"
            )
        return vector
