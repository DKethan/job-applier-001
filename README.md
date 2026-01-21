# JobCopilot - AI Job Application Copilot

A production-grade monorepo application for automating job applications with AI-powered resume tailoring and form autofill.

## Architecture

- **apps/web**: Next.js 14+ web application (App Router, TypeScript, Tailwind)
- **apps/api**: FastAPI backend (Python) with Pydantic schemas, MongoDB database
- **apps/extension**: Chrome MV3 extension for form autofill
- **packages/shared**: Shared TypeScript types (Zod schemas) and utilities
- **Database**: MongoDB (hosted MongoDB Atlas cluster)

## Prerequisites

- Node.js 20+ ([Download](https://nodejs.org/))
- pnpm 8+ (Install with: `npm install -g pnpm` or see below)
- **Python 3.11 or 3.12** (NOT 3.13 - many packages don't support it yet)
  - [Download Python 3.11](https://www.python.org/downloads/) or install via conda
- Conda or Miniconda ([Download](https://docs.conda.io/en/latest/miniconda.html)) - OR use venv
- MongoDB Atlas account (free tier works) or local MongoDB

## Installation

### Step 1: Install pnpm (if not installed)

```bash
# Option A: Using npm (recommended)
npm install -g pnpm

# Option B: Using Homebrew (macOS)
brew install pnpm

# Option C: Using curl
curl -fsSL https://get.pnpm.io/install.sh | sh -
```

Verify installation:
```bash
pnpm --version
```

### Step 2: Setup Environment Files

```bash
# Copy root .env.example
cp .env.example .env

# Copy API .env.example
cp apps/api/.env.example apps/api/.env

# Copy web .env.example
cp apps/web/.env.example apps/web/.env

# Copy extension .env.example
cp apps/extension/.env.example apps/extension/.env
```

2. **Generate secrets for API (JWT and encryption keys):**

**Option A: Use the provided script (easiest):**
```bash
python3 scripts/generate_secrets.py
```

**Option B: Generate manually:**
```bash
# Generate JWT secret (32 characters, URL-safe)
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate encryption key (32 bytes, base64 encoded)
python3 -c "import secrets; import base64; print(base64.b64encode(secrets.token_bytes(32)).decode())"
```

**Option C: Quick one-liner (generates both):**
```bash
python3 -c "import secrets, base64; print(f'JWT_SECRET={secrets.token_urlsafe(32)}'); print(f'ENCRYPTION_KEY_BASE64={base64.b64encode(secrets.token_bytes(32)).decode()}')"
```

Copy the output values to `apps/api/.env`:
- `JWT_SECRET`: Used to sign authentication tokens (prevents token tampering)
- `ENCRYPTION_KEY_BASE64`: Used to encrypt PII data at rest (protects sensitive user data)

**Why these are needed:**
- **JWT_SECRET**: Signs authentication tokens. Without it, anyone could forge login tokens.
- **ENCRYPTION_KEY_BASE64**: Encrypts sensitive data (profiles, resumes) before storing in database.

3. **Update API .env with required values:**
   - `MONGODB_URI`: Your MongoDB connection string (already set in `.env.example`)
   - `OPENAI_API_KEY`: Your OpenAI API key (get from https://platform.openai.com/api-keys)

## Local Development

### Step 3: Install Node.js Dependencies

```bash
# Install all dependencies (this installs for web, extension, and shared packages)
pnpm install

# Build shared package (required before running web app)
cd packages/shared
pnpm build
cd ../..
```

**Troubleshooting:** 
- If you get "workspace:*" errors, make sure you're using `pnpm`, not `npm`
- If you see lxml warnings about 'html-clean' extra - this is harmless, ignore it

### Step 4: Setup and Run API

```bash
cd apps/api

# IMPORTANT: Use Python 3.11 or 3.12 (NOT 3.13 - many packages don't support it yet)
# Delete existing environment if it has Python 3.13:
# conda deactivate
# conda env remove -n job-applier-001

# Create conda environment with Python 3.11
conda create -n job-applier-001 python=3.11 -y
conda activate job-applier-001

# OR if using venv (alternative):
# python3.11 -m venv job-applier-001
# source job-applier-001/bin/activate  # On Windows: job-applier-001\Scripts\activate

# Verify Python version (should be 3.11.x)
python --version

# Install Python dependencies
pip install -r requirements.txt

# Test MongoDB connection (optional)
python test_connection.py

# Run API server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: http://localhost:8000
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

**Note:** MongoDB indexes are created automatically on first run.

### Step 5: Run Web App (in a new terminal)

```bash
# Make sure you're in the project root
cd apps/web

# Run Next.js dev server
pnpm dev
```

The web app will be available at: http://localhost:3000

### Step 6: Build and Load Extension (Optional)

```bash
cd apps/extension

# Build the extension
pnpm build

# Load in Chrome:
# 1. Open Chrome and go to chrome://extensions/
# 2. Enable "Developer mode" (toggle in top right)
# 3. Click "Load unpacked"
# 4. Navigate to and select the `apps/extension/dist` directory
```

The extension will autofill job application forms when you visit application pages.

## Quick Start Summary

1. Install pnpm: `npm install -g pnpm`
2. Install Node deps: `pnpm install` (from project root)
3. Build shared package: `cd packages/shared && pnpm build && cd ../..`
4. Copy `.env.example` files to `.env` in each app
5. Create conda env with Python 3.11: `conda create -n job-applier-001 python=3.11 -y && conda activate job-applier-001`
   - **Important:** Use Python 3.11 or 3.12, NOT 3.13 (packages don't support it yet)
6. Install Python deps: `cd apps/api && pip install -r requirements.txt`
7. Generate secrets: `python3 scripts/generate_secrets.py`
8. Update `apps/api/.env` with your MongoDB URI and OpenAI API key
9. Run API: `cd apps/api && conda activate job-applier-001 && python -m uvicorn app.main:app --reload`
10. Run Web: `cd apps/web && pnpm dev` (in new terminal)

## Testing

### Run Ingest Test CLI

```bash
cd apps/api
python -m tools.ingest_test --url "https://job-boards.greenhouse.io/doordashusa/jobs/7264631"
```

This tests job posting ingestion. Make sure your `.env` file is configured with MongoDB URI.

### API Tests

```bash
cd apps/api
pytest
```

## Environment Variables

See `.env.example` files in each app directory. Copy them to `.env` and fill in required values.

**Critical variables for `apps/api/.env`:**
- `MONGODB_URI`: Already set in `.env.example` (or use your own MongoDB Atlas connection)
- `MONGODB_DB_NAME`: Database name (default: `jobcopilot`)
- `ENCRYPTION_KEY_BASE64`: Generate with `python3 scripts/generate_secrets.py`
- `JWT_SECRET`: Generate with `python3 scripts/generate_secrets.py`
- `OPENAI_API_KEY`: Get from https://platform.openai.com/api-keys

**Note:** MongoDB indexes are created automatically on first run. No manual migrations needed!

## Project Structure

```
job-applier-001/
├── apps/
│   ├── api/              # FastAPI backend
│   │   ├── app/
│   │   │   ├── routers/  # API route handlers
│   │   │   ├── services/ # Business logic
│   │   │   ├── ingestion/ # Job posting extractors
│   │   │   └── utils/    # Utilities (encryption, logging)
│   │   ├── tests/
│   │   └── tools/        # CLI tools
│   ├── web/              # Next.js app
│   │   └── app/          # App Router pages
│   └── extension/        # Chrome extension
│       └── src/          # Extension source
├── packages/
│   └── shared/           # Shared types
└── docker-compose.yml
```

## Features

- **Job Ingestion**: Supports multiple ATS providers (Greenhouse, Lever, Ashby, SmartRecruiters, Workday, Oracle CX, Avature, etc.)
- **Resume Parsing**: Extract structured profile data from PDF/DOCX resumes using LLM
- **Resume Tailoring**: AI-powered resume customization based on job descriptions
- **Document Generation**: Generate tailored resumes in DOCX and PDF formats
- **Form Autofill**: Chrome extension with intelligent field detection and confidence scoring
- **Security**: PII encryption at rest, XSS prevention, PII redaction in logs

## License

Private - All Rights Reserved
