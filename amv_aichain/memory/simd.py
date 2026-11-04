# Copyright (c) 2026 Uno Kim / AMEVA Foundation. All rights reserved.
# SPDX-License-Identifier: Apache-2.0 OR Commercial-License
"""
==============================================================================
amv-aichain SIMD Vector Engine: Native Hardware Acceleration & C-ABI Loader
==============================================================================
Provides high-performance vector operations (cosine similarity, batch scan)
utilizing ARM NEON / AVX SIMD instructions via ctypes dynamic C-ABI binding.
Gracefully and losslessly degrades to pure Python standard library if native
shared libraries are not present in the runtime environment.
Zero external heavy dependencies - Pure Python 3.10+ standard library.
"""

from __future__ import annotations
import os
import sys
import math
import ctypes
import logging
from typing import Any, Callable, List, Optional, Tuple

logger = logging.getLogger("amv_aichain.memory.simd")

# Pure Python reference implementations with full NaN/Inf protection
def py_cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Computes cosine similarity in pure Python with robust NaN/Inf guard."""
    if len(v1) != len(v2):
        raise ValueError(f"Dimension mismatch: query has dimension {len(v1)}, but candidate has dimension {len(v2)}")
    if not v1:
        return 0.0
    dot = 0.0
    norm_a = 0.0
    norm_b = 0.0
    for a, b in zip(v1, v2):
        if math.isnan(a) or math.isnan(b) or math.isinf(a) or math.isinf(b):
            return 0.0
        dot += a * b
        norm_a += a * a
        norm_b += b * b

    if norm_a <= 0.0 or norm_b <= 0.0:
        return 0.0
    denom = math.sqrt(norm_a) * math.sqrt(norm_b)
    if denom <= 0.0:
        return 0.0
    sim = dot / denom
    # Clamp float precision jitter to [-1.0, 1.0]
    return max(-1.0, min(1.0, sim))

def py_batch_cosine_similarity(query: List[float], matrix: List[List[float]]) -> List[float]:
    """Computes cosine similarity of a query vector against a matrix of vectors."""
    return [py_cosine_similarity(query, vec) for vec in matrix]


class NativeVectorEngine:
    """
    Dynamically loads and dispatches to native SIMD C-ABI vector routines
    (libameva_vector.so, libtermux_vector.so, or custom build artifacts).
    """

    def __init__(self):
        self._lib: Optional[ctypes.CDLL] = None
        self._simd_cosine_func: Optional[Callable] = None
        self._simd_batch_func: Optional[Callable] = None
        self._backend_name: str = "pure_python_stdlib"
        self._init_engine()

    def _find_library_path(self) -> Optional[str]:
        candidates = [
            # 1. Environment variable override
            os.environ.get("AMEVA_VECTOR_LIB_PATH", ""),
            # 2. Local ameva-runtime installation path in Termux
            os.path.expanduser("~/.local/share/ameva/current/lib/libameva_vector.so"),
            os.path.expanduser("~/.local/share/ameva/lib/libameva_vector.so"),
            # 3. Termux system lib path
            "/data/data/com.termux/files/usr/lib/libameva_vector.so",
            "/data/data/com.termux/files/usr/lib/libtermux_vector.so",
            # 4. Standard Linux / Android dynamic loader paths
            "libameva_vector.so",
            "libtermux_vector.so",
        ]
        for path in candidates:
            if path and os.path.isfile(path) and os.access(path, os.R_OK):
                return path
        return None

    def _init_engine(self) -> None:
        lib_path = self._find_library_path()
        if not lib_path:
            logger.debug("[simd] No native SIMD vector shared library found. Running on pure Python stdlib engine.")
            return

        try:
            self._lib = ctypes.CDLL(lib_path)
            # Bind single cosine similarity: float ameva_cosine_sim(const float* a, const float* b, int dim)
            if hasattr(self._lib, "ameva_cosine_sim"):
                func = self._lib.ameva_cosine_sim
                func.argtypes = [ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float), ctypes.c_int]
                func.restype = ctypes.c_float
                self._simd_cosine_func = func

            # Bind batch cosine similarity: void ameva_batch_cosine_sim(const float* q, const float* mat, int num, int dim, float* out)
            if hasattr(self._lib, "ameva_batch_cosine_sim"):
                bfunc = self._lib.ameva_batch_cosine_sim
                bfunc.argtypes = [
                    ctypes.POINTER(ctypes.c_float),
                    ctypes.POINTER(ctypes.c_float),
                    ctypes.c_int,
                    ctypes.c_int,
                    ctypes.POINTER(ctypes.c_float)
                ]
                bfunc.restype = None
                self._simd_batch_func = bfunc

            if self._simd_cosine_func is not None:
                self._backend_name = f"native_simd ({os.path.basename(lib_path)})"
                logger.info("[simd] Successfully initialized native SIMD vector acceleration from %s", lib_path)
        except Exception as exc:
            logger.warning("[simd] Failed to bind native vector library at %s: %s. Falling back to pure Python.", lib_path, exc)
            self._lib = None
            self._simd_cosine_func = None
            self._simd_batch_func = None
            self._backend_name = "pure_python_stdlib"

    @property
    def is_accelerated(self) -> bool:
        """Returns True if hardware native SIMD acceleration is currently active."""
        return self._simd_cosine_func is not None

    @property
    def backend_name(self) -> str:
        """Returns description of the active computational backend."""
        return self._backend_name

    def cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        """Calculates cosine similarity with automatic SIMD dispatch and graceful fallback."""
        if len(v1) != len(v2) or not v1:
            return 0.0

        if self._simd_cosine_func is not None:
            try:
                dim = len(v1)
                c_v1 = (ctypes.c_float * dim)(*v1)
                c_v2 = (ctypes.c_float * dim)(*v2)
                res = float(self._simd_cosine_func(c_v1, c_v2, dim))
                if math.isnan(res) or math.isinf(res):
                    return 0.0
                return max(-1.0, min(1.0, res))
            except Exception:
                # Fallback to pure Python on unexpected ABI fault
                pass

        return py_cosine_similarity(v1, v2)

    def batch_cosine_similarity(self, query: List[float], matrix: List[List[float]]) -> List[float]:
        """Calculates batch cosine similarity against a collection of vectors."""
        if not matrix or not query:
            return []

        if self._simd_batch_func is not None and matrix:
            dim = len(query)
            num = len(matrix)
            # Validate uniform dimensions
            if all(len(v) == dim for v in matrix):
                try:
                    c_q = (ctypes.c_float * dim)(*query)
                    flat_mat = [val for vec in matrix for val in vec]
                    c_mat = (ctypes.c_float * (dim * num))(*flat_mat)
                    c_out = (ctypes.c_float * num)()
                    self._simd_batch_func(c_q, c_mat, num, dim, c_out)
                    return [max(-1.0, min(1.0, float(c_out[i]))) for i in range(num)]
                except Exception:
                    pass

        return py_batch_cosine_similarity(query, matrix)


# Global singleton instance
_GLOBAL_SIMD_ENGINE: Optional[NativeVectorEngine] = None

def get_simd_engine() -> NativeVectorEngine:
    """Returns the shared NativeVectorEngine singleton."""
    global _GLOBAL_SIMD_ENGINE
    if _GLOBAL_SIMD_ENGINE is None:
        _GLOBAL_SIMD_ENGINE = NativeVectorEngine()
    return _GLOBAL_SIMD_ENGINE
