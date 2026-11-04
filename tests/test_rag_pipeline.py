# Copyright (c) 2026 Uno Kim / AMEVA Foundation. All rights reserved.
# SPDX-License-Identifier: Apache-2.0 OR Commercial-License
"""
Unit tests for LCEL RAG Pipeline, RunnablePassthrough, RunnableParallel,
DirectoryLoader, and SQLiteVectorStore retriever integration.
"""
from __future__ import annotations
import os
import json
import tempfile
import pytest
from pathlib import Path

from amv_aichain.core.base import (
    RunnableLambda,
    RunnablePassthrough,
    RunnableParallel,
    RunnableSequence,
)
from amv_aichain.core.splitters import (
    Document,
    DirectoryLoader,
    format_docs,
)
from amv_aichain.core.prompt import PromptTemplate
from amv_aichain.memory.sqlite import SQLiteVectorStore, VectorStoreRetriever
from amv_aichain.memory.embeddings import SparseBM25Embeddings


def test_runnable_passthrough_identity():
    passthrough = RunnablePassthrough()
    assert passthrough.invoke("test_input") == "test_input"
    assert passthrough.invoke({"key": 42}) == {"key": 42}


@pytest.mark.asyncio
async def test_runnable_passthrough_async():
    passthrough = RunnablePassthrough()
    res = await passthrough.ainvoke("async_val")
    assert res == "async_val"


def test_runnable_parallel_execution():
    parallel = RunnableParallel(
        upper=lambda x: str(x).upper(),
        length=lambda x: len(str(x)),
        echo=RunnablePassthrough(),
    )
    result = parallel.invoke("termux")
    assert result == {
        "upper": "TERMUX",
        "length": 6,
        "echo": "termux",
    }


@pytest.mark.asyncio
async def test_runnable_parallel_async_execution():
    async def async_upper(x: str) -> str:
        return x.upper()

    parallel = RunnableParallel(
        upper=async_upper,
        length=lambda x: len(x),
    )
    result = await parallel.ainvoke("android")
    assert result == {
        "upper": "ANDROID",
        "length": 7,
    }


def test_dict_coercion_in_pipe():
    # LCEL syntactic sugar: dict is automatically coerced into RunnableParallel
    chain = (
        {
            "double": lambda x: x * 2,
            "square": lambda x: x ** 2,
        }
        | RunnableLambda(lambda d: d["double"] + d["square"])
    )
    res = chain.invoke(3)
    # (3 * 2) + (3 ** 2) = 6 + 9 = 15
    assert res == 15


def test_directory_loader_recursive():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        # Create directory hierarchy
        sub_dir = tmp_path / "sub"
        sub_dir.mkdir(parents=True, exist_ok=True)

        file1 = tmp_path / "doc1.txt"
        file1.write_text("Hello from txt doc", encoding="utf-8")

        file2 = sub_dir / "doc2.md"
        file2.write_text("# Markdown Title\nContent here", encoding="utf-8")

        file3 = sub_dir / "doc3.json"
        file3.write_text(json.dumps({"info": "termux edge runtime"}), encoding="utf-8")

        # Irrelevant extension should be ignored
        file_ignored = sub_dir / "ignored.bin"
        file_ignored.write_bytes(b"\x00\x01\x02")

        loader = DirectoryLoader(tmpdir, glob="**/*", recursive=True)
        docs = loader.load()

        assert len(docs) == 3
        contents = [d.page_content for d in docs]
        assert any("Hello from txt doc" in c for c in contents)
        assert any("Markdown Title" in c for c in contents)
        assert any("termux edge runtime" in c for c in contents)

        # Check metadata
        for doc in docs:
            assert "source" in doc.metadata
            assert os.path.exists(doc.metadata["source"])


def test_format_docs_helper():
    docs = [
        Document("First paragraph", metadata={"id": 1}),
        Document("Second paragraph", metadata={"id": 2}),
    ]
    formatted = format_docs(docs)
    assert formatted == "First paragraph\n\nSecond paragraph"

    custom_formatted = format_docs(docs, separator=" --- ")
    assert custom_formatted == "First paragraph --- Second paragraph"


def test_lcel_rag_pipeline_end_to_end():
    # Setup temporary SQLiteVectorStore
    store = SQLiteVectorStore(embedding_fn=SparseBM25Embeddings(dimension=64))
    store.add_texts(
        [
            "AMEVA Sovereign Runtime is designed for mobile edge micro-clusters.",
            "Termux AIChain provides zero-dependency LCEL orchestration on Android.",
            "Linux Kernel on modern smartphones supports ARM NEON SIMD.",
        ],
        metadatas=[{"source": "docA"}, {"source": "docB"}, {"source": "docC"}],
    )

    retriever = store.as_retriever(k=2)
    assert isinstance(retriever, VectorStoreRetriever)

    # Construct standard LCEL RAG Chain:
    # { "context": retriever | format_docs, "question": RunnablePassthrough() }
    #   | prompt
    #   | fake_llm
    prompt = PromptTemplate.from_template(
        "Context:\n{context}\n\nQuestion: {question}\nAnswer:"
    )
    fake_llm = RunnableLambda(lambda p: f"EchoLLM[{p}]")

    rag_chain = (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough(),
        }
        | prompt
        | fake_llm
    )

    query = "What is Termux AIChain?"
    output = rag_chain.invoke(query)

    assert "EchoLLM[" in output
    assert "Question: What is Termux AIChain?" in output
    assert "Answer:" in output


@pytest.mark.asyncio
async def test_lcel_rag_pipeline_async():
    store = SQLiteVectorStore(embedding_fn=SparseBM25Embeddings(dimension=64))
    store.add_texts(["Edge intelligence without cloud dependencies."])

    retriever = store.as_retriever(k=1)
    rag_chain = (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough(),
        }
        | RunnableLambda(lambda d: f"Q: {d['question']} | C: {d['context'].strip()}")
    )

    res = await rag_chain.ainvoke("Edge query")
    assert "Q: Edge query" in res
    assert "Edge intelligence without cloud dependencies." in res
