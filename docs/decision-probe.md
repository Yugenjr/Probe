# Decision Probe

Decision Probe is an AI-powered platform for investigating historical incidents, post-mortems, and complex support escalations. It is optimized for unstructured data parsing, document retrieval, and timeline-based reasoning.

## Purpose
To reconstruct timelines from scattered historical data (PDFs, support tickets, system logs) and perform root cause analysis (RCA) on past outages or security incidents using a Retrieval-Augmented Generation (RAG) architecture.

## Architecture & Execution Flow
- **Frontend (`apps/frontend`)**: A React 19 application built with Next.js 15. It handles workspace management, document uploading (via `react-dropzone`), and visual timeline reconstruction. State is managed by Zustand.
- **Backend (`apps/backend`)**: A FastAPI application (`main.py`) serving the REST endpoints.
- **Persistence**: Relational data (workspaces, incident records) is persisted via SQLModel into SQLite or PostgreSQL.
- **Retrieval Engine**: Found in `apps/backend/retrieval/`, managing vector embeddings and semantic search across uploaded evidence.
- **Inference Pipeline**: Found in `apps/backend/inference/`, responsible for taking retrieved context and producing RCA hypotheses.

### Entry Point & How it Starts
The backend is initialized via `main.py` which sets up the database, mounts CORS middleware, and includes routers (e.g., `workspace_router`).
Execution:
```bash
cd apps/decision-probe/apps/backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
The frontend starts via standard Next.js scripts:
```bash
cd apps/decision-probe/apps/frontend
npm run dev
```

## Configuration & Dependencies
- **Backend Dependencies**: `fastapi`, `uvicorn`, `sqlmodel`, `pydantic-settings` (managed via `requirements.txt`).
- **Frontend Dependencies**: `next`, `react`, `shadcn`, `zustand`, `@tanstack/react-query`, `framer-motion` (managed via `package.json`).
- **Environment Variables**: Managed via `.env` files in their respective directories (API keys for embeddings/inference, database URIs).

## External Services & Databases
- Embeddings and Inference rely on external LLM providers (configured via API keys).
- Defaults to a local SQLite database (`database.db`), but production deployments can route to a PostgreSQL instance.

## Execution Flow
1. User creates a Workspace via Frontend.
2. User uploads evidence (logs, reports).
3. Backend parses documents, generates embeddings, and stores them in the Retrieval vector store.
4. User initiates an investigation.
5. Inference Engine queries the Retrieval layer to build context.
6. The reasoning pipeline generates a structured timeline and hypotheses.
7. Results are streamed back (via SSE or standard REST polling) to the frontend for visualization.

## Current Capabilities & Limitations
- **Capabilities**: Strong ingestion of unstructured text; clean workspace encapsulation; timeline generation.
- **Limitations**: Geared towards post-mortem (batch) processing rather than real-time streaming ingestion. Server-Sent Events (SSE) support requires further stabilization in the inference loop for long-running reasoning tasks.
