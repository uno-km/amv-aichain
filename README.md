# AMV-AIChain

> **마이그레이션 안내**: 이 패키지는 `termux-aichain`에서 `amv-aichain`로 이름이 바뀌었습니다. 기존 `termux-aichain` 배포본(PyPI/npm)은 호환을 위해 당분간 유지되나 deprecated 상태이며 더 이상 갱신되지 않습니다. `pip install amv-aichain` / `npm install amv-aichain`로 전환하십시오.
>
> Android **Termux 환경** 또는 **안드로이드 Linux 커널(루팅 없이 Linux 환경이 구동되는 모든 디바이스)** 에서 동작합니다 — Termux 전용이 아닙니다.

[![PyPI](https://img.shields.io/pypi/v/amv-aichain.svg?style=flat-square&color=0369a1)](https://pypi.org/project/amv-aichain/)
[![Python](https://img.shields.io/pypi/pyversions/amv-aichain.svg?style=flat-square)](https://pypi.org/project/amv-aichain/)
[![npm](https://img.shields.io/npm/v/amv-aichain.svg?style=flat-square&color=b91c1c)](https://www.npmjs.com/package/amv-aichain)
[![npm downloads](https://img.shields.io/npm/dm/amv-aichain.svg?style=flat-square&color=b91c1c)](https://www.npmjs.com/package/amv-aichain)
[![License](https://img.shields.io/badge/License-Apache_2.0-004499.svg?style=flat-square)](https://github.com/uno-km/amv-aichain)

> **왜 터먹스에선 랭체인 대신 AIChain인가? 수백MB 의존성 폭탄 vs 94KB 제로-의존성 LCEL 및 하드웨어 액추에이션**  
> *Why LangChain on Termux? Bloat & Crash vs 94KB Zero-Dep LCEL & Hardware Native Agents*

---

## Architecture & Overview

외부 의존성 0개(Zero-Dependency)의 순수 표준 라이브러리 기반으로 LangChain 호환 LCEL 파이프 체이닝(prompt | llm | parser), StateGraph 자율 에이전트, 온디바이스 SQLite 코사인 벡터 검색, 스마트폰 하드웨어 직접 제어(배터리, 온도, 진동, GPS)를 94KB 초경량 코어로 완벽히 제공합니다.

AMV-AIChain provides 100% pure standard-library LCEL pipe chaining (prompt | llm | parser), autonomous StateGraph agents, on-device SQLite vector RAG, and first-class Android smartphone hardware actuation (battery, temperature, haptics, GPS) in a tiny 94KB footprint.

---

## Installation & Quickstart

### Python (PyPI)
```bash
pip install amv-aichain
```
```python
from amv_aichain import PromptTemplate, OpenAICompatibleChat, StringOutputParser, get_battery_status

# 1. Read physical smartphone hardware telemetry
battery = get_battery_status()

# 2. Build LCEL Chain connected to local llama-server (port 8080)
prompt = PromptTemplate.from_template("Phone Telemetry: {status}. Diagnose in 1 sentence:")
llm = OpenAICompatibleChat(base_url="http://127.0.0.1:8080/v1", model="llama3", temperature=0.3)
chain = prompt | llm | StringOutputParser()

# 3. Execute with 0 external dependencies
report = chain.invoke({"status": battery})
print("AI Diagnostic:", report)
```

### Node.js / TypeScript (npm)
```bash
npm install amv-aichain
```
```typescript
import { PromptTemplate, OpenAICompatibleChat, StringOutputParser, getBatteryStatus } from 'amv-aichain';

// 1. Read physical smartphone hardware telemetry
const battery = await getBatteryStatus.func();

// 2. Build LCEL Chain connected to local llama-server (port 8080)
const prompt = PromptTemplate.fromTemplate('Phone Telemetry: {status}. Diagnose in 1 sentence:');
const llm = new OpenAICompatibleChat({ baseUrl: 'http://127.0.0.1:8080/v1', model: 'llama3', temperature: 0.3 });
const chain = prompt.pipe(llm).pipe(new StringOutputParser());

// 3. Execute with 0 npm dependencies
const report = await chain.invoke({ status: JSON.stringify(battery) });
console.log('AI Diagnostic:', report);
```

---

## Official Documentation & Benchmarks
- [Official Architecture & API Reference](https://uno-km.vercel.app/lib/aichain/)
- [Ecosystem Metrics & Registry Stats](https://uno-km.vercel.app/foundation/metrics)
- [AMEVA Open-Source Foundation Portal](https://uno-km.vercel.app/foundation/index.html)

---

## License
Licensed under the Apache-2.0 License. Copyright (c) 2026 Eunho Kim ([@uno-km](https://github.com/uno-km)).
