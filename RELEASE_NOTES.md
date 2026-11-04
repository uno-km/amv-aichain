# v2.0.0 (2026-11-04) — Python import name follows the amv-aichain package name

### Changed
- The Python package is now `amv_aichain` (previously `termux_aichain`). Code, CLI entry points, scripts, docs and cross-package references use the amv-* names.
- `import termux_aichain` keeps working through a deprecated alias that returns the same module objects and emits a `DeprecationWarning`. The alias will be removed in a future major release.

### Unchanged
- On-disk cache and data directories (for example `~/.cache/termux-*`) keep their names, so models already downloaded on devices stay in use.
- Termux platform commands (`termux-tts-speak`, `termux-wake-lock`, `termux-api`, ...) keep their names.

---

# v1.2.0 (2026-10-13) — Fail-Fast Zero-Silent-Exception & ameva-runtime v2 Integration

Eliminated all silent exception handlers across 136 unit tests, migrated hardware acceleration to ameva-runtime v2, and integrated cluster orchestrator adapter.

### Key Changes
- Purged all bare except:pass blocks and subprocess exception black holes (136 unit tests verified).
- Migrated hardware acceleration dependency to ameva-runtime v2.
- Integrated AMEVA cluster orchestrator control-plane adapter.
- Added live Snapdragon S25 and Exynos A53 E2E telemetry recipes.

---

# 📦 Termux-AIChain v1.1.0 Release Notes

> **Release Date**: August 27, 2026  
> **Release Tag**: `aichain-v1.1.0` (Git: `v1.1.0`)  
> **Security Audit & Verification**: 153/153 Automated Tests Passed (Zero Failures / Zero Errors)

---

## 🚀 Key Highlights
- **Fail-Closed Identity Verification & Upstream Capability Matching**: Multi-model enumeration and strict model identifier validation when connecting to `llama-server`, `BitNet.cpp`, and OpenAI-compatible backends.
- **ToolPolicy Parity**: Enforced `ToolPolicy(default="deny")`, JSON Schema parameter validation, and user approval callbacks across Python and Node.js runtimes.
- **TypeScript SSOT & Zero-Drift Build System**: Consolidated `js/src/**/*.ts` as the single source of truth with automated validation against ESM distribution artifacts.

---

## 📋 Changelog

### ✨ Features
- **Fail-Closed Server Identity Verifier (`ServerIdentityVerifier` / `verifyServerIdentity`)**:
  - Multi-backend support across `termux-aichain`, `llama-server`, `bitnet-server`, and generic `openai-compatible` endpoints.
  - Automatic capability fallback inspection via `/v1/models` when `/health` returns generic `status: "ok"`.
  - Verifier Dependency Injection (`options.identityVerifier`) for isolated unit testing.
- **Tool Permission Security Model**:
  - Default `ToolPolicy(default="deny")` applied to `create_react_agent` / `createReactAgent`.
  - Strict JSON Schema validation for tool arguments and asynchronous approval callbacks (`approval_callback` / `approvalCallback`).
- **Android Native Diagnostic Fallback**:
  - Direct Linux kernel sysfs inspection (`/sys/class/power_supply/battery`) when `termux-api` is absent.

### 🐛 Bug Fixes
- **Upstream Server Connection Protocol Alignment**: Removed hardcoded protocol version assertions in `LocalAgent.local()` and `cmd_status`, unifying capability negotiation via server profiles.
- **Multi-Model Discovery**: Scans the complete `data` array in `/v1/models` to match `expected_model_id` on multi-model servers.
- **README Character Encoding**: Restored clean UTF-8 encoding for ASCII banners and symbols.

### ⚡ Performance & Security
- **Loopback CORS & Payload Bounds**: Strict loopback URL validation, 413 Payload Too Large responses when exceeding `max_body_bytes`, and constant-time `timingSafeEqual` token checks.
- **Memory & Runtime Efficiency**: Cold start 12.8ms, RSS memory 14.2MB, zero external runtime dependencies.

---

## 📦 Package Distribution & Verification

| Platform | Package Name | Install Command | SHA-256 Checksum |
|:---|:---|:---|:---|
| **npm** | `termux-aichain` | `npm install termux-aichain@1.1.0` | `a0f719bf419908ece841c02924561fa008eaca28348c7ee296151550f82298c1` |
| **PyPI (wheel)** | `termux-aichain` | `pip install termux-aichain==1.1.0` | `d53fbab4694ccc43acc1f222f1f02b2236ef8c3a6f6369bcc54d8c68dbada1a1` |
| **PyPI (sdist)** | `termux-aichain` | `pip install termux-aichain==1.1.0` | `f7587ee3a226e3ef7cd00fd0ec2be6ad8e0fd0e8612dd3c2b1e831ff90d2fe07` |

---

## 🔗 Official Documentation
- **Official Docs**: [https://uno-km.vercel.app/lib/aichain/](https://uno-km.vercel.app/lib/aichain/)
- **API Reference**: [https://uno-km.vercel.app/lib/aichain/](https://uno-km.vercel.app/lib/aichain/)
