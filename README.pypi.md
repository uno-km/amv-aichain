# Termux-AIChain (Python)

[![PyPI](https://img.shields.io/pypi/v/termux-aichain.svg?style=flat-square&color=0369a1)](https://pypi.org/project/termux-aichain/)
[![Python](https://img.shields.io/pypi/pyversions/termux-aichain.svg?style=flat-square)](https://pypi.org/project/termux-aichain/)
[![License](https://img.shields.io/badge/License-Apache_2.0-004499.svg?style=flat-square)](https://github.com/uno-km/termux-aichain)

> Why LangChain on Termux? Bloat & Crash vs 94KB Zero-Dep LCEL & Hardware Native Agents

## Installation

```bash
pip install termux-aichain
```

## Quickstart

```python
from termux_aichain import PromptTemplate, OpenAICompatibleChat, StringOutputParser, get_battery_status

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

## Description
Termux-AIChain provides 100% pure standard-library LCEL pipe chaining (prompt | llm | parser), autonomous StateGraph agents, on-device SQLite vector RAG, and first-class Android smartphone hardware actuation (battery, temperature, haptics, GPS) in a tiny 94KB footprint.

## Documentation
- [Official Documentation & API Reference](https://uno-km.vercel.app/lib/aichain/)
- [GitHub Repository](https://github.com/uno-km/termux-aichain)

## License
Apache-2.0 License. Copyright (c) 2026 Eunho Kim (@uno-km).
