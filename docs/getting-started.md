# Getting Started

Follow these steps to run the Probe platform locally on your machine.

## Prerequisites
- **Python**: 3.10+ (managed via `pip` / `venv` or `poetry`)
- **Node.js**: 20+ (for the frontend, managed via `npm` or `pnpm`)
- **Docker**: For running supporting infrastructure (PostgreSQL, Vector DBs).

## Step 1: Install Shared SDK
The SDK must be installed first, as both applications depend on it.

```bash
cd packages/driftguard-sdk
pip install -r requirements.txt
pip install -e .
```

## Step 2: Configure Environment Variables
Copy the `.env.example` files to `.env` in the following locations and populate them with your API keys:
- `packages/driftguard-sdk/.env`
- `apps/driftguard-probe/.env`
- `apps/decision-probe/apps/backend/.env`

Ensure you set `DRIFTGUARD_DEFAULT_API_KEY` and your preferred LLM provider key (e.g., `OPENAI_API_KEY`).

## Step 3: Start the DriftGuard SDK Gateway
This will initialize the shared database schema.

```bash
cd packages/driftguard-sdk
uvicorn main:app --reload --port 8002
```

## Step 4: Run Decision Probe
In a new terminal, start the backend API:
```bash
cd apps/decision-probe/apps/backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

In another terminal, start the frontend UI:
```bash
cd apps/decision-probe/apps/frontend
npm install
npm run dev
```
The UI will be available at `http://localhost:3000`.

## Step 5: Run DriftGuard Probe
In a new terminal, run the autonomous investigation engine:
```bash
cd apps/driftguard-probe
pip install -r requirements.txt
python run_first_real_investigation.py
```
This script acts as a test harness, simulating a drift event and triggering the Supervisor agent.
