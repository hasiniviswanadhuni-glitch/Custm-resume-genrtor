# Customize Resume Generation

> **AI-Powered Explainable Resume Customization Using User Profile and Job Description Analysis**  
> *Evidence-Grounded • Explainable • User-Controlled • Fact-Preserving*

---

## Overview

**Customize Resume Generation** is a full-stack platform that analyzes a candidate's structured master profile against target job descriptions, computes transparent ATS match scores, generates explainable AI suggestions grounded strictly in user-provided facts, and exports professional, job-specific ATS-friendly PDF and DOCX resumes.

### Core Differentiator
- **Zero Hallucinations:** Every statement, skill, and metric is verified against candidate evidence. Missing skills are flagged as learning opportunities—never fabricated.
- **Master Profile Isolation:** The master profile is the candidate's immutable source of truth. Job-specific resumes are derived snapshots.
- **Transparent Explainability:** Every recommendation explains *What*, *Why*, *Triggering Requirement*, *Candidate Evidence*, and *Confidence*.
- **Candidate Autonomy:** The user has full control to Accept, Reject, or Edit suggestions before export.

---

## Architecture

```text
               +------------------------------------+
               |      Next.js 14+ App Router        |
               |      (TypeScript + Tailwind UI)    |
               +-----------------+------------------+
                                 | REST JSON API
               +-----------------v------------------+
               |        FastAPI Backend API         |
               |   (Port 8000 / OpenAPI / Docs)     |
               +--------+------------------+--------+
                        |                  |
       +----------------v---+         +----v-----------------+
       | NLP & AI Engines   |         | Database Layer       |
       | - JD Analyzer      |         | - Supabase Postgres  |
       | - Semantic Matcher |         | - SQLAlchemy Models  |
       | - Fact Guard       |         | - RLS & Migrations   |
       | - Document Exporter|         +----------------------+
       +--------------------+
```

---

## Quick Start (Running Locally)

### 1. Prerequisites
- Python 3.11+
- Node.js 18+ (Node 24 LTS installed)

### 2. Run Backend (FastAPI)
```powershell
# In repository root:
$env:PYTHONPATH="."
py -3.11 backend/run_server.py
```
Backend API will start at **http://localhost:8000**  
Interactive API Docs (Swagger UI): **http://localhost:8000/docs**

### 3. Run Frontend (Next.js)
```powershell
cd frontend
$env:PATH = "C:\Program Files\nodejs;" + $env:PATH
& "C:\Program Files\nodejs\npm.cmd" run start
```
Frontend web application will run at **http://localhost:3000**

---

## Automated Test Suite & Backtesting

Run all 15 automated test suites:
```powershell
$env:PYTHONPATH="."
py -3.11 -m pytest backend/tests -v
```

### Verified Test Suites:
1. `test_ai_hallucination_prevention.py`: Section 34 anti-hallucination verification.
2. `test_deep_audit_backtesting.py`: 7-point exhaustive backtesting of all core features.
3. `test_api_e2e.py`: Complete 10-step API user journey lifecycle.
4. `test_matching_engine.py`: Exact, related, partial, and missing skill classifications.
5. `test_jd_analyzer.py`: Multi-stage NLP parsing and taxonomy extraction.
6. `test_resume_customizer.py`: Priority re-ranking and master profile isolation.
7. `test_export_service.py`: Server-side PDF (`reportlab`) and Word DOCX (`python-docx`) generation.

---

## Documentation Links

- [Deep Audit & Backtesting Report](docs/DEEP_AUDIT_AND_BACKTESTING_REPORT.md)
- [API Integration Guide (Supabase, Gemini, OpenAI)](docs/API_INTEGRATION_GUIDE.md)
- [Supabase Initial SQL Schema Migration](backend/supabase/migrations/001_initial_schema.sql)
