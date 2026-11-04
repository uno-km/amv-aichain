# AMV-AIChain (Node.js & TypeScript)

[![npm](https://img.shields.io/npm/v/amv-aichain.svg?style=flat-square&color=b91c1c)](https://www.npmjs.com/package/amv-aichain)
[![npm downloads](https://img.shields.io/npm/dm/amv-aichain.svg?style=flat-square&color=b91c1c)](https://www.npmjs.com/package/amv-aichain)
[![License](https://img.shields.io/badge/License-Apache_2.0-004499.svg?style=flat-square)](https://github.com/uno-km/amv-aichain)

> Why LangChain on Termux? Bloat & Crash vs 94KB Zero-Dep LCEL & Hardware Native Agents

## Installation

```bash
npm install amv-aichain
```

## Quickstart

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

## Description
AMV-AIChain provides 100% pure standard-library LCEL pipe chaining (prompt | llm | parser), autonomous StateGraph agents, on-device SQLite vector RAG, and first-class Android smartphone hardware actuation (battery, temperature, haptics, GPS) in a tiny 94KB footprint.

## Documentation
- [Official Documentation & API Reference](https://uno-km.vercel.app/lib/aichain/)
- [GitHub Repository](https://github.com/uno-km/amv-aichain)

## License
Apache-2.0 License. Copyright (c) 2026 Eunho Kim (@uno-km).
