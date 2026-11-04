# Copyright (c) 2026 Uno Kim / AMEVA Foundation. All rights reserved.
# SPDX-License-Identifier: Apache-2.0 OR Commercial-License
"""
==============================================================================
amv-aichain Core Text Splitters & Micro Document Loaders
==============================================================================
Provides hierarchical recursive chunking and edge file loaders.
Zero external heavy dependencies - Pure Python 3.10+ standard library.
"""

from __future__ import annotations
import os
import json
import re
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterator, List, Optional, Sequence, Union

@dataclass
class Document:
    page_content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    score: Optional[float] = None

    @property
    def content(self) -> str:
        return self.page_content

    def __getitem__(self, item: int) -> Any:
        if item == 0:
            return self
        elif item == 1:
            return self.score if self.score is not None else 0.0
        raise IndexError("Document tuple index out of range (use 0 for doc, 1 for score)")

    def __repr__(self) -> str:
        snippet = self.page_content[:50].replace("\n", " ")
        return f"Document(content='{snippet}...', metadata={self.metadata})"

class BaseTextSplitter:
    """Base class for text chunk splitters."""

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        length_function: Callable[[str], int] = len,
        keep_separator: bool = False
    ):
        if chunk_overlap >= chunk_size:
            raise ValueError(f"chunk_overlap ({chunk_overlap}) must be strictly less than chunk_size ({chunk_size})")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.length_function = length_function
        self.keep_separator = keep_separator

    def split_text(self, text: str) -> List[str]:
        raise NotImplementedError

    def split_documents(self, documents: Sequence[Document]) -> List[Document]:
        result: List[Document] = []
        for doc in documents:
            chunks = self.split_text(doc.page_content)
            for i, chunk in enumerate(chunks):
                meta = dict(doc.metadata)
                meta["chunk_index"] = i
                result.append(Document(page_content=chunk, metadata=meta))
        return result

    def create_documents(self, texts: Sequence[str], metadatas: Optional[Sequence[Dict[str, Any]]] = None) -> List[Document]:
        docs: List[Document] = []
        for i, text in enumerate(texts):
            meta = metadatas[i] if metadatas and i < len(metadatas) else {}
            chunks = self.split_text(text)
            for j, chunk in enumerate(chunks):
                c_meta = dict(meta)
                c_meta["chunk_index"] = j
                docs.append(Document(page_content=chunk, metadata=c_meta))
        return docs

class CharacterTextSplitter(BaseTextSplitter):
    """Splits text along a single separator with overlap."""

    def __init__(self, separator: str = "\n\n", **kwargs: Any):
        super().__init__(**kwargs)
        self.separator = separator

    def split_text(self, text: str) -> List[str]:
        splits = text.split(self.separator) if self.separator else list(text)
        return self._merge_splits(splits, self.separator)

    def _merge_splits(self, splits: List[str], separator: str) -> List[str]:
        docs: List[str] = []
        current_doc: List[str] = []
        total_len = 0
        sep_len = self.length_function(separator)

        for s in splits:
            s_len = self.length_function(s)
            if current_doc and total_len + sep_len + s_len > self.chunk_size:
                merged = separator.join(current_doc)
                if merged.strip():
                    docs.append(merged)
                # Handle overlap
                while current_doc and total_len > self.chunk_overlap:
                    popped = current_doc.pop(0)
                    total_len -= (self.length_function(popped) + sep_len)
            current_doc.append(s)
            total_len += s_len + (sep_len if len(current_doc) > 1 else 0)

        if current_doc:
            merged = separator.join(current_doc)
            if merged.strip():
                docs.append(merged)
        return docs

class RecursiveCharacterTextSplitter(BaseTextSplitter):
    """Hierarchical text splitter using decreasing granularity separators."""

    def __init__(
        self,
        separators: Optional[List[str]] = None,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        **kwargs: Any
    ):
        super().__init__(chunk_size=chunk_size, chunk_overlap=chunk_overlap, **kwargs)
        self.separators = separators or ["\n\n", "\n", ". ", "? ", "! ", " ", ""]

    def split_text(self, text: str) -> List[str]:
        return self._split_recursive(text, self.separators)

    def _split_recursive(self, text: str, separators: List[str]) -> List[str]:
        final_chunks: List[str] = []
        separator = separators[-1]
        new_separators: List[str] = []

        for i, _s in enumerate(separators):
            if _s == "":
                separator = ""
                break
            if _s in text:
                separator = _s
                new_separators = separators[i + 1:]
                break

        splits = text.split(separator) if separator else list(text)

        good_splits: List[str] = []
        for s in splits:
            if self.length_function(s) < self.chunk_size:
                good_splits.append(s)
            else:
                if good_splits:
                    merged = self._merge_splits(good_splits, separator)
                    final_chunks.extend(merged)
                    good_splits = []
                if not new_separators:
                    final_chunks.append(s)
                else:
                    other_chunks = self._split_recursive(s, new_separators)
                    final_chunks.extend(other_chunks)

        if good_splits:
            merged = self._merge_splits(good_splits, separator)
            final_chunks.extend(merged)

        return final_chunks

    def _merge_splits(self, splits: List[str], separator: str) -> List[str]:
        docs: List[str] = []
        current_doc: List[str] = []
        total_len = 0
        sep_len = self.length_function(separator)

        for s in splits:
            s_len = self.length_function(s)
            if current_doc and total_len + sep_len + s_len > self.chunk_size:
                merged = separator.join(current_doc)
                if merged.strip():
                    docs.append(merged)
                while current_doc and total_len > self.chunk_overlap:
                    popped = current_doc.pop(0)
                    total_len -= (self.length_function(popped) + sep_len)
            current_doc.append(s)
            total_len += s_len + (sep_len if len(current_doc) > 1 else 0)

        if current_doc:
            merged = separator.join(current_doc)
            if merged.strip():
                docs.append(merged)
        return docs

# ==============================================================================
# Micro Edge Document Loaders
# ==============================================================================

class BaseLoader:
    def load(self) -> List[Document]:
        raise NotImplementedError

class TextLoader(BaseLoader):
    """Loads plain text files with automatic encoding detection fallback."""

    def __init__(self, file_path: str, encoding: str = "utf-8"):
        self.file_path = file_path
        self.encoding = encoding

    def load(self) -> List[Document]:
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"File not found: {self.file_path}")
        try:
            with open(self.file_path, "r", encoding=self.encoding) as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(self.file_path, "r", encoding="latin-1") as f:
                content = f.read()
        return [Document(page_content=content, metadata={"source": self.file_path, "filename": os.path.basename(self.file_path)})]

class MarkdownLoader(TextLoader):
    """Loads markdown files."""
    pass

class JSONLoader(BaseLoader):
    """Loads JSON file and extracts specific jq-like keys or dumps content."""

    def __init__(self, file_path: str, content_key: Optional[str] = None):
        self.file_path = file_path
        self.content_key = content_key

    def load(self) -> List[Document]:
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"File not found: {self.file_path}")
        with open(self.file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        docs: List[Document] = []
        if isinstance(data, list):
            for i, item in enumerate(data):
                if self.content_key and isinstance(item, dict) and self.content_key in item:
                    text = str(item[self.content_key])
                else:
                    text = json.dumps(item, ensure_ascii=False)
                docs.append(Document(page_content=text, metadata={"source": self.file_path, "index": i}))
        elif isinstance(data, dict):
            if self.content_key and self.content_key in data:
                text = str(data[self.content_key])
            else:
                text = json.dumps(data, ensure_ascii=False)
            docs.append(Document(page_content=text, metadata={"source": self.file_path}))
        return docs

class DirectoryLoader(BaseLoader):
    """Recursively scans and loads all documents in a directory."""

    SUPPORTED_TEXT_EXTENSIONS = {
        ".txt", ".log", ".csv", ".py", ".js", ".ts", ".html",
        ".xml", ".yaml", ".yml", ".ini", ".env", ".rst"
    }

    def __init__(
        self,
        path: str,
        glob: str = "**/*",
        recursive: bool = True,
        silent_errors: bool = False,
        loader_cls: Optional[Any] = None
    ):
        self.path = path
        self.glob = glob
        self.recursive = recursive
        self.silent_errors = silent_errors
        self.loader_cls = loader_cls

    def load(self) -> List[Document]:
        import glob as _glob
        if not os.path.exists(self.path):
            raise FileNotFoundError(f"Directory not found: {self.path}")

        pattern = os.path.join(self.path, self.glob)
        matched_files = _glob.glob(pattern, recursive=self.recursive)
        docs: List[Document] = []

        for fpath in sorted(matched_files):
            if not os.path.isfile(fpath):
                continue
            ext = os.path.splitext(fpath)[1].lower()
            try:
                if self.loader_cls is not None:
                    loader: BaseLoader = self.loader_cls(fpath)
                elif ext in (".md", ".markdown"):
                    loader = MarkdownLoader(fpath)
                elif ext == ".json":
                    loader = JSONLoader(fpath)
                elif ext in self.SUPPORTED_TEXT_EXTENSIONS:
                    loader = TextLoader(fpath)
                else:
                    # Skip unrecognized/binary extensions when loader_cls is not specified
                    continue
                docs.extend(loader.load())
            except Exception as ex:
                if not self.silent_errors:
                    raise RuntimeError(f"Error loading {fpath}: {ex}") from ex
        return docs

def format_docs(docs: Sequence[Document], separator: str = "\n\n") -> str:
    """Utility formatter assembling a list of Documents into a single context string."""
    return separator.join(doc.page_content for doc in docs)