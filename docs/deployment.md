# Deployment Guide for SupportMind

SupportMind is architected for zero-friction local development, containerized production deployments via Docker Compose, and free-tier cloud hosting on Render or Vercel.

---

## 1. Quickstart: Local Docker Compose (Recommended)

Run both the FastAPI backend and React frontend with a single command:

```bash
# Clone the repository
git clone https://github.com/your-username/SupportMind.git
cd SupportMind

# (Optional) Provide Gemini API key in .env or run with offline demo mode
cp .env.example .env

# Build and start services
docker compose up --build
```

- **Frontend App**: [http://localhost:5173](http://localhost:5173)
- **Backend API Docs (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Backend Health Check**: [http://localhost:8000/api/health](http://localhost:8000/api/health)

---

## 2. Local Manual Setup (Without Docker)

### Terminal 1: Backend
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r backend/requirements.txt
uvicorn app.main:app --app-dir backend --reload --port 8000
```

### Terminal 2: Frontend
```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:5173](http://localhost:5173). The Vite dev server automatically proxies `/api` requests to `http://127.0.0.1:8000`.

---

## 3. Cloud Deployment: Render (Blueprint)

This repository includes a [`render.yaml`](../render.yaml) blueprint declaring:
1. `supportmind-backend`: Python Web Service with automatic SQLite seeding and RAG indexing.
2. `supportmind-frontend`: Static Site hosting the compiled React + Vite bundle.

### Steps:
1. Fork or push this repository to your GitHub account.
2. Go to [Render Dashboard](https://dashboard.render.com/) -> **New** -> **Blueprint**.
3. Connect your GitHub repository.
4. Set optional environment variable:
   - `GEMINI_API_KEY`: *(Optional)* Your Google AI Studio API key. If omitted, SupportMind automatically operates in grounded offline demo mode.
5. Click **Apply**. Render will build and deploy both services automatically.

---

## 4. Alternative: Vercel Frontend + Render Backend

1. Deploy the Backend to Render as a Python Web Service (`buildCommand: pip install -r backend/requirements.txt`, `startCommand: uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 10000`).
2. Deploy the `frontend/` directory to Vercel:
   - Framework Preset: **Vite**
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `dist`
3. Update the backend proxy URL in [`vercel.json`](../vercel.json) to your live Render backend URL.

---

## 5. Environment Variables Reference

| Variable | Description | Default | Required? |
| :--- | :--- | :--- | :--- |
| `GEMINI_API_KEY` | Google Gemini API Key for LLM reasoning | `""` (Offline Demo Fallback) | No |
| `LLM_MODEL` | Gemini Model Identifier | `gemini-2.5-flash` | No |
| `PROMPT_VERSION` | Strategy version (`v1`, `v2`, or `v3`) | `v3` | No |
| `DEMO_MODE` | Force offline responses for reproducible demos | `true` | No |
| `ENVIRONMENT` | Runtime environment (`development`, `test`, `production`) | `production` | No |
| `ALLOWED_ORIGINS`| CORS allowed origin URLs | `http://localhost:5173,http://localhost:3000` | No |
