# Copyright (c) 2026 Uno Kim / AMEVA Foundation. All rights reserved.
# SPDX-License-Identifier: Apache-2.0 OR Commercial-License
"""
==============================================================================
amv-aichain: Sovereign Zero-Dependency Edge AI Framework for Termux & Android
==============================================================================
Copyright (c) 2026 AMEVA Open-Source Foundation & UnoKim.
Licensed under the Apache License, Version 2.0.
"""

from __future__ import annotations
import importlib
from typing import Any

__version__ = "2.0.0"
__author__ = "UnoKim <uno-km@users.noreply.github.com>"

_LAZY_IMPORTS = {
    # Schema
    "Message": ("amv_aichain.core.schema", "Message"),
    "HumanMessage": ("amv_aichain.core.schema", "HumanMessage"),
    "AIMessage": ("amv_aichain.core.schema", "AIMessage"),
    "SystemMessage": ("amv_aichain.core.schema", "SystemMessage"),
    "ToolMessage": ("amv_aichain.core.schema", "ToolMessage"),
    "UsageInfo": ("amv_aichain.core.schema", "UsageInfo"),
    "GenerationResult": ("amv_aichain.core.schema", "GenerationResult"),
    "StreamChunk": ("amv_aichain.core.schema", "StreamChunk"),
    # Prompt
    "PromptTemplate": ("amv_aichain.core.prompt", "PromptTemplate"),
    "ChatPromptTemplate": ("amv_aichain.core.prompt", "ChatPromptTemplate"),
    # Base
    "Runnable": ("amv_aichain.core.base", "Runnable"),
    "RunnableLambda": ("amv_aichain.core.base", "RunnableLambda"),
    "RunnableSequence": ("amv_aichain.core.base", "RunnableSequence"),
    "RunnablePassthrough": ("amv_aichain.core.base", "RunnablePassthrough"),
    "RunnableParallel": ("amv_aichain.core.base", "RunnableParallel"),
    "BaseChatModel": ("amv_aichain.core.base", "BaseChatModel"),
    # Providers
    "OpenAICompatibleChat": ("amv_aichain.core.providers.openai_compatible", "OpenAICompatibleChat"),
    "BitNetChat": ("amv_aichain.core.providers.bitnet", "BitNetChat"),
    "LocalServerConfig": ("amv_aichain.core.providers.local_server", "LocalServerConfig"),
    "LocalServerManager": ("amv_aichain.core.providers.local_server", "LocalServerManager"),
    "LlamaCppServer": ("amv_aichain.core.providers.local_server", "LlamaCppServer"),
    "BitNetServer": ("amv_aichain.core.providers.local_server", "BitNetServer"),
    # Enterprise LocalAgent & 4 Execution Modes
    "LocalAgent": ("amv_aichain.core.local_agent", "LocalAgent"),
    "AgentState": ("amv_aichain.core.agent_types", "AgentState"),
    "ConnectConfig": ("amv_aichain.core.agent_types", "ConnectConfig"),
    "ManagedConfig": ("amv_aichain.core.agent_types", "ManagedConfig"),
    "EmbeddedConfig": ("amv_aichain.core.agent_types", "EmbeddedConfig"),
    "RemoteConfig": ("amv_aichain.core.agent_types", "RemoteConfig"),
    "ToolPolicy": ("amv_aichain.core.agent_types", "ToolPolicy"),
    "ToolRule": ("amv_aichain.core.agent_types", "ToolRule"),
    "ToolCallCandidate": ("amv_aichain.core.agent_types", "ToolCallCandidate"),
    "TransportSecurityConfig": ("amv_aichain.core.agent_types", "TransportSecurityConfig"),
    # Output Normalization
    "OutputNormalizer": ("amv_aichain.output.normalizer", "OutputNormalizer"),
    "RawModelResponse": ("amv_aichain.output.normalizer", "RawModelResponse"),
    "NormalizedModelResponse": ("amv_aichain.output.normalizer", "NormalizedModelResponse"),
    # Standard Errors
    "LocalAgentError": ("amv_aichain.core.agent_types", "LocalAgentError"),
    "ServerConnectionRefusedError": ("amv_aichain.core.agent_types", "ServerConnectionRefusedError"),
    "ServerProtocolMismatchError": ("amv_aichain.core.agent_types", "ServerProtocolMismatchError"),
    "ModelIdentityMismatchError": ("amv_aichain.core.agent_types", "ModelIdentityMismatchError"),
    "ManagedSpawnNotSupportedError": ("amv_aichain.core.agent_types", "ManagedSpawnNotSupportedError"),
    "ServerStartupTimeoutError": ("amv_aichain.core.agent_types", "ServerStartupTimeoutError"),
    "DuplicateServerOwnershipError": ("amv_aichain.core.agent_types", "DuplicateServerOwnershipError"),
    "RemoteFallbackNotAuthorizedError": ("amv_aichain.core.agent_types", "RemoteFallbackNotAuthorizedError"),
    "ToolApprovalRequiredError": ("amv_aichain.core.agent_types", "ToolApprovalRequiredError"),
    "ToolArgumentValidationError": ("amv_aichain.core.agent_types", "ToolArgumentValidationError"),
    "ToolRateLimitExceededError": ("amv_aichain.core.agent_types", "ToolRateLimitExceededError"),
    "ToolPolicyDeniedError": ("amv_aichain.core.agent_types", "ToolPolicyDeniedError"),
    "ToolCallRepairNotAllowedError": ("amv_aichain.core.agent_types", "ToolCallRepairNotAllowedError"),
    "DuplicateToolAliasError": ("amv_aichain.core.agent_types", "DuplicateToolAliasError"),
    "NativeBackendUnavailableError": ("amv_aichain.core.agent_types", "NativeBackendUnavailableError"),
    # Parsers
    "StringOutputParser": ("amv_aichain.core.parsers", "StringOutputParser"),
    "JsonOutputParser": ("amv_aichain.core.parsers", "JsonOutputParser"),
    "RegexOutputParser": ("amv_aichain.core.parsers", "RegexOutputParser"),
    # Splitters
    "Document": ("amv_aichain.core.splitters", "Document"),
    "CharacterTextSplitter": ("amv_aichain.core.splitters", "CharacterTextSplitter"),
    "RecursiveCharacterTextSplitter": ("amv_aichain.core.splitters", "RecursiveCharacterTextSplitter"),
    "TextLoader": ("amv_aichain.core.splitters", "TextLoader"),
    "MarkdownLoader": ("amv_aichain.core.splitters", "MarkdownLoader"),
    "JSONLoader": ("amv_aichain.core.splitters", "JSONLoader"),
    "DirectoryLoader": ("amv_aichain.core.splitters", "DirectoryLoader"),
    "format_docs": ("amv_aichain.core.splitters", "format_docs"),
    # Graph
    "StateGraph": ("amv_aichain.graph.state", "StateGraph"),
    "CompiledGraph": ("amv_aichain.graph.state", "CompiledGraph"),
    "START": ("amv_aichain.graph.state", "START"),
    "END": ("amv_aichain.graph.state", "END"),
    "Tool": ("amv_aichain.graph.agent", "Tool"),
    "tool": ("amv_aichain.graph.agent", "tool"),
    "create_react_agent": ("amv_aichain.graph.agent", "create_react_agent"),
    # Memory
    "ConversationBufferMemory": ("amv_aichain.memory.buffer", "ConversationBufferMemory"),
    "SQLiteEntityMemory": ("amv_aichain.memory.sqlite", "SQLiteEntityMemory"),
    "SQLiteVectorStore": ("amv_aichain.memory.sqlite", "SQLiteVectorStore"),
    "VectorStoreRetriever": ("amv_aichain.memory.sqlite", "VectorStoreRetriever"),
    "NativeVectorEngine": ("amv_aichain.memory.simd", "NativeVectorEngine"),
    "get_simd_engine": ("amv_aichain.memory.simd", "get_simd_engine"),
    "FactExtractor": ("amv_aichain.memory.extractor", "FactExtractor"),
    "BaseEmbeddings": ("amv_aichain.memory.embeddings", "BaseEmbeddings"),
    "LocalEmbeddings": ("amv_aichain.memory.embeddings", "LocalEmbeddings"),
    "SparseBM25Embeddings": ("amv_aichain.memory.embeddings", "SparseBM25Embeddings"),
    # Serve
    "AgentServer": ("amv_aichain.serve.server", "AgentServer"),
    "serve": ("amv_aichain.serve.server", "serve"),
    "DASHBOARD_HTML": ("amv_aichain.serve.dashboard", "DASHBOARD_HTML"),
    # Trace
    "TraceSpan": ("amv_aichain.trace.tracer", "TraceSpan"),
    "Tracer": ("amv_aichain.trace.tracer", "Tracer"),
    "traceable": ("amv_aichain.trace.tracer", "traceable"),
    # Device Tools
    "get_battery_status": ("amv_aichain.device.tools", "get_battery_status"),
    "get_sensor_data": ("amv_aichain.device.tools", "get_sensor_data"),
    "get_device_location": ("amv_aichain.device.tools", "get_device_location"),
    "record_speech_to_text": ("amv_aichain.device.tools", "record_speech_to_text"),
    "vibrate_device": ("amv_aichain.device.tools", "vibrate_device"),
    "send_notification": ("amv_aichain.device.tools", "send_notification"),
    "speak_tts": ("amv_aichain.device.tools", "speak_tts"),
    "execute_shell": ("amv_aichain.device.tools", "execute_shell"),
    "get_default_device_tools": ("amv_aichain.device.tools", "get_default_device_tools"),
    # Ecosystem Tools
    "infer_bitnet_llm": ("amv_aichain.device.ecosystem", "infer_bitnet_llm"),
    "transcribe_speech": ("amv_aichain.device.ecosystem", "transcribe_speech"),
    "generate_diffusion_image": ("amv_aichain.device.ecosystem", "generate_diffusion_image"),
    "browse_web_headless": ("amv_aichain.device.ecosystem", "browse_web_headless"),
    "synthesize_speech": ("amv_aichain.device.ecosystem", "synthesize_speech"),
    "speak_text": ("amv_aichain.device.ecosystem", "speak_text"),
    "analyze_image_vlm": ("amv_aichain.device.ecosystem", "analyze_image_vlm"),
    "detect_faces": ("amv_aichain.device.ecosystem", "detect_faces"),
    "detect_edges_canny": ("amv_aichain.device.ecosystem", "detect_edges_canny"),
    "get_ecosystem_tools": ("amv_aichain.device.ecosystem", "get_ecosystem_tools"),
}

__all__ = ["__version__"] + list(_LAZY_IMPORTS.keys())

def __getattr__(name: str) -> Any:
    if name in _LAZY_IMPORTS:
        module_path, attr_name = _LAZY_IMPORTS[name]
        mod = importlib.import_module(module_path)
        val = getattr(mod, attr_name)
        globals()[name] = val
        return val
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

def __dir__() -> list[str]:
    return sorted(list(globals().keys()) + list(_LAZY_IMPORTS.keys()))
