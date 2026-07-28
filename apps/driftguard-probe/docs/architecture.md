# Architecture Overview — DriftGuard Probe

## The Platform-Agnostic Paradigm
DriftGuard Probe is engineered around strict domain isolation and inversion of control.  
Instead of binding tightly to DriftGuard's internal REST models, Probe treats DriftGuard as our **Reference First Adapter**. The architecture permits any observability suite (Arize, WhyLabs, Custom Monitors) to connect to Probe's core reasoning engine by implementing standard protocols defined under `probe/interfaces/`.

```
[ MLOps Platform (DriftGuard, Arize) ]
                  │
        Webhook / Event Emit
                  ▼
         [ Probe API Gateway ]
                  │
      [ Supervisor & Workflows ]
                  │
        [ Specialized Agents ]
                  │
           [ Tool Registry ]
                  │
         [ Platform Adapter ] ──► (REST/MCP Call to Observability Suite)
```

## Core Subsystems
- **`probe.interfaces`**: Pure Python Protocol abstractions for LLMs, tools, memory, adapters, and persistence.
- **`probe.workflows`**: Declarative state machines orchestrating domain investigations without altering supervisor agent logic.
- **`probe.core.state` & `lifecycle`**: Explicit domain states (`CollectingEvidence`, `Researching`, `Completed`) ensuring traceability and replayability.
- **`probe.events`**: An asynchronous pub/sub event bus supporting distributed telemetry and OpenTelemetry spans.
- **`probe.llm`**: Modular provider gateway featuring structured schema output parsing and tenacity retry pipelines.
