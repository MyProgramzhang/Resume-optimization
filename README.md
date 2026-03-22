# Resume Agent

Local MVP for a resume optimization agent with:

- Vue 3 frontend for upload, status polling, and result display
- FastAPI backend for PDF parsing, job orchestration, and LLM integration
- Side-by-side before/after diff rendering

## Project Structure

```text
frontend/  Vue 3 + Vite + TypeScript app
backend/   FastAPI app, SQLite job store, PDF parser, LLM workflow
```

## Backend Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -e .[dev]
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

Notes:

- `USE_MOCK_LLM=true` lets the full flow run without a real API key.
- Set `USE_MOCK_LLM=false` and provide `MODEL_API_KEY` to use a real OpenAI-compatible endpoint.
- For Alibaba Bailian `qwen-plus`, use `MODEL_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1`.
- `MODEL_ENABLE_THINKING=false` is a good default for JSON-focused resume parsing and rewriting tasks.
- V1 only supports text-based PDF resumes.

## Frontend Setup

```bash
cd frontend
copy .env.example .env
cmd /c npm install
cmd /c npm run dev
```

The frontend runs at `http://localhost:5173` by default and expects the backend at `http://localhost:8000`.

## API Endpoints

- `POST /api/jobs`
- `GET /api/jobs/{job_id}`
- `GET /api/jobs/{job_id}/result`
- `GET /api/jobs/{job_id}/optimized-pdf`
- `GET /api/health`

## Test and Validation

Backend syntax check:

```bash
python -m compileall backend\app
```

Backend tests after installing dependencies:

```bash
cd backend
pytest
```

## Current V1 Limits

- No OCR support for scanned PDFs
- Exported PDF is generated from structured content and does not preserve the original visual template
- Single-user local workflow only
- Mock mode uses lightweight heuristic outputs for local smoke testing
