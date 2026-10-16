# v1.3.0 (2026-10-14) — LCEL RAG Pipeline, SIMD Vector Acceleration & Parallel StateGraph

Delivered 1st-class LCEL RAG abstractions, C-ABI dynamic SIMD vector acceleration engine, parallel Fan-Out/Fan-In StateGraph execution with State Reducer, and complete Python & Node.js ESM test suite expansion (171 pytest + 21 node:test 100% Pass).

### Key Changes
- **LCEL RAG Pipeline**: Added `RunnablePassthrough`, `RunnableParallel` with automatic dictionary pipe coercion, `DirectoryLoader` recursive scanner, and `format_docs` context formatter.
- **SIMD Vector Engine**: Implemented `termux_aichain.memory.simd` with dynamic C-ABI loader for ARM NEON SIMD vector cosine similarity, zero-overhead stdlib fallback, and strict NaN/Inf boundary protections.
- **Parallel StateGraph Concurrency**: Extended `StateGraph` to support multi-target Fan-Out & Fan-In concurrently via `ThreadPoolExecutor` (sync) and `asyncio.gather` (async), accompanied by deep State Reducer for concurrent state merging.
- **Retriever Integration**: Implemented `SQLiteVectorStore.as_retriever()` and `MicroVectorStore.asRetriever()` across Python and TypeScript/Node.js ESM for seamless 1-line RAG chaining.
- **Strict Test Coverage**: Expanded unit tests to 171 Python test cases and 21 Node.js ESM test cases with 100% pass rate.

---

# v1.2.0 (2026-10-13) — Fail-Fast Zero-Silent-Exception & ameva-runtime v2 Integration

Eliminated all silent exception handlers across 136 unit tests, migrated hardware acceleration to ameva-runtime v2, and integrated cluster orchestrator adapter.

### Key Changes
- Purged all bare except:pass blocks and subprocess exception black holes (136 unit tests verified).
- Migrated hardware acceleration dependency to ameva-runtime v2.
- Integrated AMEVA cluster orchestrator control-plane adapter.
- Added live Snapdragon S25 and Exynos A53 E2E telemetry recipes.

---

# Changelog

All notable changes to 	ermux-aichain will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.5] - 2026-10-06

### Changed
- Comprehensive documentation revamp with top-mounted LangChain vs Mobile comparison.
- Full-stack verified on physical Samsung Galaxy S25 (Snapdragon 8 Elite) and Galaxy A53 (Exynos 1280).
- Pure zero-dependency stdlib architecture with native Android actuator tools.
- Strict OpenSSF and CNCF compliance audit across Python and Node.js ESM.

---

## [1.1.4] - 2026-09-05

### Changed
- Synchronized unified orchestration dependencies and ecosystem service telemetry.
- Validated full-stack zero-regression test suite compatibility.

---

## [1.1.3] - 2026-09-05

### Changed
- Migrated hardware acceleration dependency to unified `ameva-runtime>=2.0.0` and `@ameva/runtime>=2.0.0`.
- Enhanced chain execution error reporting with fail-fast validation.

---

## [1.1.1] - 2026-09-02

### Added
- **Graph Agent Workflow**: State-graph based local autonomous agent orchestration.
- **Hardware Diagnostics Tools**: Native sensor, battery, and network telemetry bindings for Termux:API.

### Fixed
- **Subprocess Error Logging**: Eliminated exception black hole in _run_cmd with explicit TimeoutExpired, FileNotFoundError, and PermissionError logging.
- **Termux API Service Monitor**: Added returncode inspection and warning logs in _ensure_termux_api_service_alive.

### Verification
- **Unit Tests**: 136 / 136 passed with 100% assertion coverage.