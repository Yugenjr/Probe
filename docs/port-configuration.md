# Platform Port Configuration

The Probe platform consists of multiple independently running backends and frontends. To prevent startup crashes (specifically `EADDRINUSE` or `HTTP 404` routing errors), the platform ports have been explicitly mapped to never collide.

## API / Backend Services

| Service | Protocol | Port | Working Directory | Configured In |
|---------|----------|------|-------------------|---------------|
| **DriftGuard SDK** (Platform Gateway) | HTTP/REST | **8000** | `packages/driftguard-sdk` | Default Uvicorn / Hardcoded across 50+ test files |
| **Decision Probe Backend** | HTTP/REST | **8005** | `apps/decision-probe/apps/backend` | `main.py`, `package.json` |
| **DriftGuard Probe API** (Docker Compose) | HTTP/REST | **8002** | `apps/driftguard-probe/docker` | `docker-compose.yml` (Port mapping `8002:8000`) |

## Frontend / User Interfaces

| Service | Framework | Port | Working Directory | Configured In |
|---------|-----------|------|-------------------|---------------|
| **Decision Probe Frontend** | Next.js | **3000** | `apps/decision-probe/apps/frontend` | Next.js Default |
| **DriftGuard Probe UI** | Vite/React | **3002** | `apps/driftguard-probe/ui` | `vite.config.ts` |

---

## Important Routing Notes

> [!WARNING]
> **DriftGuard Probe UI Proxy**
> The `driftguard-probe/ui` runs on **3002**, but its internal Vite proxy routes all `/api/*` calls to **8002**. This ensures the UI properly communicates with the Dockerized DriftGuard Probe engine without hitting CORS issues.

> [!CAUTION]
> **Real-Time Investigation Script**
> The test script `run_first_real_investigation.py` explicitly connects to `http://localhost:8000`. This requires the **DriftGuard SDK** to be actively running on port 8000. If the SDK is not running, the script will crash with a `HTTP 404: Not Found` error.
