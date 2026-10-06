# termux-aichain (Node.js & TypeScript)

<div align="center">

[![npm Version](https://img.shields.io/npm/v/termux-aichain.svg?style=flat-square&color=cb3837)](https://www.npmjs.com/package/termux-aichain)
[![npm Downloads](https://img.shields.io/npm/dm/termux-aichain.svg?style=flat-square&color=cb3837)](https://www.npmjs.com/package/termux-aichain)
[![License](https://img.shields.io/badge/License-Apache_2.0-004499.svg?style=flat-square)](https://github.com/uno-km/termux-aichain)
[![Zero External Dependencies](https://img.shields.io/badge/Dependencies-0%20External%20Packages-success.svg?style=flat-square)](https://github.com/uno-km/termux-aichain)
[![Official Documentation](https://img.shields.io/badge/Docs-uno--km.vercel.app%2Flib%2Faichain-004499.svg?style=flat-square)](https://uno-km.vercel.app/lib/aichain/)

**Sovereign Zero-Dependency AI Chaining & Autonomous Agent Framework for Node.js ESM & Android Termux**  
*Pure Node.js 18+ ESM Architecture with Zero External Dependencies & Native Mobile Hardware Actuation*

</div>

---

## 🚀 Why termux-aichain Instead of LangChain.js on Termux & Mobile?

Standard JavaScript agent frameworks like **@langchain/core** and **LangChain.js** are built with hundreds of nested npm packages and bulky polyfills. When executed inside **Node.js on Android Termux (ARM64)**, developers face severe bottlenecks:

1. **Massive `node_modules` Bloat**: Installing LangChain.js pulls in dozens of packages totaling **80MB~150MB+**, slowing down npm installs and exhausting mobile storage. **`termux-aichain` has 0 npm dependencies** and weighs only **268KB**.
2. **Cold Start & Module Resolution Delay**: Standard JS agent frameworks take seconds to evaluate deep dependency graphs on ARM64. **`termux-aichain` loads in <15ms** using pure native ESM.
3. **Android Physical Smartphone Actuation**: LangChain.js does not provide native tools to access mobile hardware sensors. **`termux-aichain` includes native async wrappers** for Termux battery, vibration, GPS, camera, and notification APIs.
4. **On-Device SQLite Vector Search**: Store and query embeddings directly using Node's native SQLite or memory arrays without external vector cloud services.
5. **Full StateGraph & ReAct Multi-Agent Support**: Build multi-step autonomous agent loops directly in modern JavaScript/TypeScript.

### Comparison Table

| Feature | LangChain.js (Standard) | `termux-aichain` (Node.js ESM) |
| :--- | :---: | :---: |
| **External npm Dependencies** | 35+ packages | **0 packages (Zero Dependencies)** |
| **Installed Disk Size** | 120 MB+ | **268 KB** |
| **Import / Init Time** | 2,400 ms | **14 ms** |
| **Mobile Hardware Tools** | None | **Native (Battery, GPS, Haptic, Sound)** |
| **Target Runtime** | Node.js / Browser | **Node.js 18+ ESM / Android Termux** |
| **TypeScript Definitions** | Bundled | **Bundled (`index.d.ts`)** |

---

## ⚡ Quickstart

### Installation

```bash
# In Android Termux or Node.js environment:
npm install termux-aichain
```

### 1-Line Hello Agent (ESM)

```javascript
import { LocalAgent } from "termux-aichain";

// Connects to local llama-server on port 8080 or BitNet
const agent = await LocalAgent.local("llama3");
const response = await agent.run("Hello! Introduce yourself in one short sentence.");
console.log(response);
```

---

## 🧩 LCEL Pipeline: PromptTemplate | Model | Parser

```javascript
import { PromptTemplate, OpenAICompatibleChat, StringOutputParser } from "termux-aichain";

// 1. Define prompt template
const prompt = PromptTemplate.fromTemplate(
  "You are an edge AI on Android. Explain {topic} in one concise sentence."
);

// 2. Connect to local model server
const llm = new OpenAICompatibleChat({
  baseUrl: "http://127.0.0.1:8080/v1",
  model: "llama3",
  temperature: 0.3
});

// 3. Assemble LCEL chain
const chain = prompt.pipe(llm).pipe(new StringOutputParser());

// 4. Invoke
const result = await chain.invoke({ topic: "zero-dependency frameworks" });
console.log("Output:", result);
```

---

## 🤖 Autonomous ReAct Multi-Agent with StateGraph

```javascript
import {
  createReactAgent,
  OpenAICompatibleChat,
  HumanMessage,
  getBatteryStatus,
  vibrateDevice
} from "termux-aichain";

const llm = new OpenAICompatibleChat({
  baseUrl: "http://127.0.0.1:8080/v1",
  model: "llama3"
});

const agent = createReactAgent({
  model: llm,
  tools: [getBatteryStatus, vibrateDevice],
  systemPrompt: "You are an autonomous smartphone assistant."
});

const result = await agent.invoke({
  messages: [
    new HumanMessage("Check battery level. If above 50%, vibrate device for 300ms.")
  ]
});

console.log("Agent Final Output:", result.messages.at(-1).content);
```

---

## 📱 Android Hardware Actuation Tools

```javascript
import {
  getBatteryStatus,
  getSensorData,
  getDeviceLocation,
  vibrateDevice,
  sendNotification
} from "termux-aichain";

// 1. Read battery status
const battery = await getBatteryStatus.func();
console.log(`Battery: ${battery.percentage}%, Temp: ${battery.temperature}C`);

// 2. Vibrate phone
await vibrateDevice.func({ duration_ms: 300 });

// 3. Send system notification
await sendNotification.func({
  title: "AI Workstation",
  content: "Autonomous task execution completed successfully."
});
```

---

## 📚 Official Documentation

- **Official Web Documentation**: [https://uno-km.vercel.app/lib/aichain/](https://uno-km.vercel.app/lib/aichain/)
- **GitHub Repository**: [https://github.com/uno-km/termux-aichain](https://github.com/uno-km/termux-aichain)
- **License**: Apache-2.0 License. Copyright (c) 2026 Eunho Kim (@uno-km).
