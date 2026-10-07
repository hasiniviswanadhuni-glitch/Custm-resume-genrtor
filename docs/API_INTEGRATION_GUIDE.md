# External API Integration Guide

This guide explains how to connect external Cloud APIs (Database and LLM Providers) to the **Customize Resume Generation** platform.

The system is engineered as an adaptable modular architecture:
- **Out-of-the-Box (Current Working State):** Operates standalone using the local SQLite engine and deterministic NLP engine (no paid external keys required to run).
- **Production Connected State:** Seamlessly plugs into Supabase PostgreSQL, Google Gemini API, or OpenAI API by populating `.env`.

---

## 1. Supabase PostgreSQL Integration

### Step 1: Create a Supabase Project
1. Go to [https://supabase.com](https://supabase.com) and log in.
2. Click **New Project** and set a database password.

### Step 2: Apply the Schema Migration
1. In the Supabase Dashboard, navigate to the **SQL Editor** tab (left sidebar).
2. Open the file `backend/supabase/migrations/001_initial_schema.sql` from this repository.
3. Paste the SQL contents into the Supabase SQL editor and click **Run**.
4. This will create:
   - All 13 relational tables (`profiles`, `education`, `skills`, `projects`, `experience`, `certifications`, `achievements`, `job_descriptions`, `job_requirements`, `skill_matches`, `ai_suggestions`, `resume_versions`, `exports`).
   - Foreign key constraints with cascading deletes.
   - Performance indexes.
   - Row Level Security (RLS) policies.

### Step 3: Configure Environment Variables
In the project root `.env` file, update:
```env
# Database Connection URL (From Supabase Project Settings -> Database -> Connection string URI)
DATABASE_URL=postgresql://postgres.[YOUR-PROJECT-REF]:[YOUR-PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres?sslmode=require

# Supabase Client Credentials
SUPABASE_URL=https://[YOUR-PROJECT-REF].supabase.co
SUPABASE_KEY=[YOUR-SUPABASE-ANON-KEY]
```

Restart the backend server (`py -3.11 backend/run_server.py`), and it will immediately connect to your live Supabase PostgreSQL database.

---

## 2. AI Provider Integration (NVIDIA NIM, Gemini, OpenAI)

The platform currently includes a high-precision, deterministic evidence-grounded engine that ensures **zero hallucinations** even without third-party API keys.

To optionally connect external cloud LLMs:

### Option A: NVIDIA NIM (Recommended Free & Low-Latency LLM)
NVIDIA provides free API credits upon signup at **[https://build.nvidia.com](https://build.nvidia.com)** with ultra-fast inference hosted on TensorRT-LLM and NVIDIA H100s.
1. Sign in to [build.nvidia.com](https://build.nvidia.com).
2. Generate an API Key (starts with `nvapi-...`).
3. In `.env`, add:
   ```env
   NVIDIA_API_KEY=nvapi-your-key-here
   NVIDIA_MODEL=meta/llama-3.1-8b-instruct
   NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
   AI_PROVIDER=hybrid
   ```

**Why `meta/llama-3.1-8b-instruct`?**
- **Latency:** ~30–50ms Time-To-First-Token (fastest among instruction models).
- **Quality:** High adherence to negative constraints (refuses to invent fake facts).
- **Cost:** Free credits with generous rate limits.

### Option B: Google Gemini API
1. Obtain an API key from Google AI Studio: [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey).
2. In `.env`, set:
   ```env
   GEMINI_API_KEY=AIzaSy...your_gemini_key_here
   AI_PROVIDER=gemini
   ```

### Option C: OpenAI API
1. Obtain an API key from OpenAI: [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys).
2. In `.env`, set:
   ```env
   OPENAI_API_KEY=sk-proj-...your_openai_key_here
   AI_PROVIDER=openai
   ```

### Option C: Hybrid Mode (Default)
```env
AI_PROVIDER=hybrid
```
When keys are supplied, the system enriches suggestions with external LLMs, while **all outputs pass through the strict `evidence_validator.py` guardrail** to guarantee that Rules 1-10 (no invented jobs, skills, degrees, or metrics) are strictly enforced before display.

---

## 3. Frontend API Target (Next.js)

If you deploy the backend to a remote server (e.g. Render, Railway, AWS ECS, Fly.io):
1. In `frontend/.env.local` (or root `.env`), set:
   ```env
   NEXT_PUBLIC_API_URL=https://your-backend-api-domain.com/api
   ```
2. Re-build the frontend with `npm run build`.

---

## 4. Summary of Configuration Keys

| Key | Description | Default / Example |
| :--- | :--- | :--- |
| `DATABASE_URL` | PostgreSQL or SQLite connection URI | `sqlite:///./resume_project.db` |
| `SUPABASE_URL` | Supabase project URL | `https://xyzcompany.supabase.co` |
| `SUPABASE_KEY` | Supabase Anon or Service Key | `eyJhbGciOi...` |
| `GEMINI_API_KEY` | Google Gemini API Key | `AIzaSy...` |
| `OPENAI_API_KEY` | OpenAI API Key | `sk-proj-...` |
| `AI_PROVIDER` | Suggestion provider strategy | `hybrid` (`hybrid`, `gemini`, `openai`, `deterministic`) |
| `SECRET_KEY` | Application encryption secret | Random 32+ character string |
| `STORAGE_DIR` | PDF/DOCX storage folder | `./storage/exports` |
