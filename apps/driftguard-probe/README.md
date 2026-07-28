# DriftGuard Probe — Autonomous ML Investigation Engine

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Code Style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

**DriftGuard Probe** is a production-grade, open-source, **platform-agnostic Autonomous ML Investigation Engine**.  
It helps MLOps and AI engineers automatically investigate production ML incidents by orchestrating specialized AI reasoning agents and infrastructure workflows.

---

## What is Probe?
Probe is **not** an observability dashboard. Probe is **not** a metrics monitor or drift detector.  
Instead, Probe takes action **after** an incident is reported by an MLOps platform (such as DriftGuard, Arize, or WhyLabs). It systematically gathers evidence, searches documentation and historical telemetry, generates hypotheses, designs experiments, and presents actionable recommendations.

### Key Capabilities
- **Platform Agnostic Inversion of Control**: Communicates via abstract interfaces (`PlatformAdapter`). DriftGuard serves as the reference first platform implementation.
- **Workflow-Driven Supervisor**: Orchestrates structured domain investigations (Drift, Bias, Security, Compliance) rather than hardcoding agent step logic.
- **MCP Native Architecture**: Designed from the ground up for seamless compatibility with the Model Context Protocol (MCP).
- **Extensibility & Plugins**: Dynamic registries allow developers to load new agents, LLM providers, tools, and adapters via zero-overhead plugins.
- **OpenTelemetry-Ready**: Built-in event bus and trace spans ensure multi-agent reasoning loops remain completely observable.

---

## Quickstart
1. Clone the repository and install dependencies:
   ```bash
   pip install -e .[dev]
   ```
2. Configure environment variables:
   ```bash
   cp .env.example .env
   ```
3. Run unit tests to verify your local installation:
   ```bash
   pytest
   ```
4. Start the Probe API Gateway:
   ```bash
   python scripts/start_probe.py
   ```
   The engine will be accessible at `http://localhost:8001`.
