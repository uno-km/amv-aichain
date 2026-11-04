# Copyright (c) 2026 Uno Kim / AMEVA Foundation. All rights reserved.
# SPDX-License-Identifier: Apache-2.0 OR Commercial-License
"""
==============================================================================
amv-aichain Core Engine: BitNet Local HTTP Server Provider Adapter
==============================================================================
Specialized HTTP client provider for BitNet local inference servers (bitnet.cpp / llama.cpp server)
communicating via OpenAI-compatible REST API endpoint (default: http://127.0.0.1:8080/v1).
Pure Python standard library implementation with zero external dependencies.
"""

from __future__ import annotations
from typing import Any, Dict, Optional
from amv_aichain.core.providers.openai_compatible import OpenAICompatibleChat

class BitNetChat(OpenAICompatibleChat):
    """HTTP Client Provider Adapter for local BitNet inference server endpoints."""

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8080/v1",
        model: str = "bitnet-b1.58-3b",
        temperature: float = 0.1,
        max_tokens: int = 256,
        timeout: float = 60.0
    ):
        super().__init__(
            base_url=base_url,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout
        )