# Deployment Guide

The Probe platform is designed to be deployed as a suite of containerized microservices.

## Docker Support
Both applications (`decision-probe` and `driftguard-probe`) and the `driftguard-sdk` contain standard `Dockerfile` definitions.
The SDK utilizes a `docker/` folder and `docker-compose` patterns for unified local deployment.

## Required External Services
To deploy the full platform, the following services must be provisioned:
1. **Database**: PostgreSQL 14+ (or SQLite for local development).
2. **Vector Store**: Qdrant, Pinecone, or pgvector for the Retrieval Engine in Decision Probe.
3. **Observability**: Prometheus (for scraping SDK metrics) and Grafana (for dashboards).
4. **LLM Provider**: OpenAI, Anthropic, or a locally hosted model (via Ollama/vLLM) to power the AI Agents.

## Environment Variables
Key environment variables required across the platform include:
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB` (Database connection strings).
- `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` (For agent inference).
- `DRIFTGUARD_DEFAULT_API_KEY` (To secure the SDK gateway).
- `CORS_ALLOWED_ORIGINS` (To secure frontend-backend communication).

## Deployment Order
When deploying to a Kubernetes cluster or via Docker Compose, services must start in the following order:
1. PostgreSQL (Wait for readiness).
2. Prometheus / Vector DB.
3. DriftGuard SDK Gateway (Provides database schema initialization).
4. Decision Probe Backend & DriftGuard Probe Engine.
5. Decision Probe Frontend.
