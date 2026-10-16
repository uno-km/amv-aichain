# Copyright (c) 2026 Uno Kim / AMEVA Foundation. All rights reserved.
# SPDX-License-Identifier: Apache-2.0 OR Commercial-License
"""
Unit tests for SIMD vector acceleration engine, cosine similarity fallback,
and robust boundary condition handling (zero vectors, NaN/Inf, dimension mismatch).
"""
from __future__ import annotations
import math
import pytest
from termux_aichain.memory.simd import (
    py_cosine_similarity,
    NativeVectorEngine,
    get_simd_engine,
)
from termux_aichain.memory.sqlite import SQLiteVectorStore
from termux_aichain.memory.embeddings import SparseBM25Embeddings


def test_cosine_similarity_basic():
    vec_a = [1.0, 0.0, 0.0]
    vec_b = [1.0, 0.0, 0.0]
    vec_c = [0.0, 1.0, 0.0]
    vec_d = [-1.0, 0.0, 0.0]

    # Identical
    assert pytest.approx(py_cosine_similarity(vec_a, vec_b), 1e-6) == 1.0
    # Orthogonal
    assert pytest.approx(py_cosine_similarity(vec_a, vec_c), 1e-6) == 0.0
    # Opposite
    assert pytest.approx(py_cosine_similarity(vec_a, vec_d), 1e-6) == -1.0


def test_cosine_similarity_zero_vector():
    zero_vec = [0.0, 0.0, 0.0]
    normal_vec = [1.0, 2.0, 3.0]
    # Division by zero should safely yield 0.0 without throwing
    assert py_cosine_similarity(zero_vec, normal_vec) == 0.0
    assert py_cosine_similarity(zero_vec, zero_vec) == 0.0


def test_cosine_similarity_nan_inf_protection():
    nan_vec = [float("nan"), 1.0, 2.0]
    inf_vec = [float("inf"), 1.0, 2.0]
    normal_vec = [1.0, 2.0, 3.0]

    # NaN / Inf should be intercepted and return 0.0 safely
    assert py_cosine_similarity(nan_vec, normal_vec) == 0.0
    assert py_cosine_similarity(inf_vec, normal_vec) == 0.0


def test_cosine_similarity_dimension_mismatch():
    vec_3d = [1.0, 2.0, 3.0]
    vec_4d = [1.0, 2.0, 3.0, 4.0]
    with pytest.raises(ValueError, match="Dimension mismatch"):
        py_cosine_similarity(vec_3d, vec_4d)


def test_native_vector_engine_batch():
    engine = NativeVectorEngine()
    query = [1.0, 0.0, 0.0]
    candidates = [
        [1.0, 0.0, 0.0],   # score 1.0
        [0.0, 1.0, 0.0],   # score 0.0
        [0.7071, 0.7071, 0.0],  # score ~0.7071
    ]

    scores = engine.batch_cosine_similarity(query, candidates)
    assert len(scores) == 3
    assert pytest.approx(scores[0], 1e-4) == 1.0
    assert pytest.approx(scores[1], 1e-4) == 0.0
    assert pytest.approx(scores[2], 1e-4) == 0.7071


def test_singleton_get_simd_engine():
    e1 = get_simd_engine()
    e2 = get_simd_engine()
    assert e1 is e2
    assert isinstance(e1, NativeVectorEngine)


def test_sqlite_vector_store_with_simd_engine():
    """Verify SQLiteVectorStore functions properly with SIMD acceleration engine."""
    store = SQLiteVectorStore(embedding_fn=SparseBM25Embeddings(dimension=64))
    texts = [
        "Termux high performance computing with ARM NEON",
        "Mobile deep learning model quantization",
        "Android operating system IPC mechanisms",
    ]
    metadatas = [{"idx": 0}, {"idx": 1}, {"idx": 2}]
    store.add_texts(texts, metadatas=metadatas)

    # 1. Similarity search
    results = store.similarity_search("NEON acceleration", k=2)
    assert len(results) == 2
    assert any("NEON" in doc.page_content for doc in results)

    # 2. Similarity search with score
    results_with_score = store.similarity_search_with_score("NEON acceleration", k=1)
    doc, score = results_with_score[0]
    assert 0.0 <= score <= 1.0

    # 3. Hybrid search (BM25 + Cosine)
    hybrid_results = store.hybrid_search("Termux Android computing", k=2, alpha=0.5)
    assert len(hybrid_results) == 2
    assert any("Android" in doc.page_content for doc in hybrid_results)
