"""Tests for the fastembed wrapper. The real model is replaced, so nothing is downloaded."""

import numpy as np
import pytest

from mini_company_brain import embedding
from mini_company_brain.embedding import BGE_QUERY_PREFIX, EMBEDDING_DIM, FastEmbedEmbedder


class RecordingModel:
    """Stands in for fastembed.TextEmbedding and records what it was asked to embed."""

    def __init__(self, model_name, cache_dir, dim=EMBEDDING_DIM):
        self.model_name = model_name
        self.cache_dir = cache_dir
        self.dim = dim
        self.seen: list[str] = []

    def embed(self, texts):
        for text in texts:
            self.seen.append(text)
            yield np.ones(self.dim, dtype=np.float32)


@pytest.fixture
def fake_model(monkeypatch):
    holder = {}

    def factory(model_name, cache_dir, **kwargs):
        holder["model"] = RecordingModel(model_name, cache_dir)
        return holder["model"]

    monkeypatch.setattr(embedding, "TextEmbedding", factory)
    return holder


def test_model_not_loaded_until_first_use(fake_model, tmp_path):
    # A re-run where every file is unchanged should not pay for loading the model.
    embedder = FastEmbedEmbedder(tmp_path)
    assert "model" not in fake_model
    embedder.embed_passages(["a"])
    assert "model" in fake_model


def test_loads_bge_small_into_given_cache_dir(fake_model, tmp_path):
    FastEmbedEmbedder(tmp_path).embed_passages(["a"])
    assert fake_model["model"].model_name == "BAAI/bge-small-en-v1.5"
    assert fake_model["model"].cache_dir == str(tmp_path)


def test_query_prefix_added_once(fake_model, tmp_path):
    FastEmbedEmbedder(tmp_path).embed_query("How much leave?")
    assert fake_model["model"].seen == [BGE_QUERY_PREFIX + "How much leave?"]


def test_passages_have_no_prefix(fake_model, tmp_path):
    vectors = FastEmbedEmbedder(tmp_path).embed_passages(["a", "b"])
    assert fake_model["model"].seen == ["a", "b"]
    assert len(vectors) == 2
    assert vectors[0].shape == (EMBEDDING_DIM,)


def test_wrong_dimension_raises(monkeypatch, tmp_path):
    monkeypatch.setattr(
        embedding,
        "TextEmbedding",
        lambda model_name, cache_dir, **kw: RecordingModel(model_name, cache_dir, dim=768),
    )
    with pytest.raises(RuntimeError, match="384"):
        FastEmbedEmbedder(tmp_path).embed_passages(["a"])
