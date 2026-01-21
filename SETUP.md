# Quick Setup Guide

## Prerequisites Check

```bash
# Check Node.js (need v20+)
node --version

# Check Python (need v3.11 or 3.12, NOT 3.13)
python3 --version
# If it shows 3.13, you'll need to install Python 3.11 separately or use conda

# Check conda (install if missing)
conda --version || echo "Install Miniconda from https://docs.conda.io/en/latest/miniconda.html"

# Check pnpm (install if missing)
pnpm --version || npm install -g pnpm
```

## Step-by-Step Setup

### 1. Install pnpm

```bash
npm install -g pnpm
```

Or if npm doesn't work:
```bash
curl -fsSL https://get.pnpm.io/install.sh | sh -
```

### 2. Install Node.js dependencies

```bash
# From project root
pnpm install
```

### 3. Build shared package

```bash
cd packages/shared
pnpm build
cd ../..
```

### 4. Setup environment files

```bash
# Copy all .env.example files
cp .env.example .env
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.example apps/web/.env
```

### 5. Generate secrets

```bash
python3 scripts/generate_secrets.py
```

Copy the output to `apps/api/.env`:
- Replace `JWT_SECRET=CHANGE_ME` with the generated JWT_SECRET
- Replace `ENCRYPTION_KEY_BASE64=CHANGE_ME_32_BYTES_BASE64` with the generated key

### 6. Update MongoDB and OpenAI keys

Edit `apps/api/.env`:
- `MONGODB_URI` is already set (or update with your own)
- `OPENAI_API_KEY` - get from https://platform.openai.com/api-keys

### 7. Setup Python environment

**⚠️ IMPORTANT: Use Python 3.11 or 3.12, NOT 3.13!**

Many packages (lxml, pydantic-core) don't support Python 3.13 yet.

**Option A: Using conda (recommended)**
```bash
cd apps/api

# If you already created environment with Python 3.13, remove it first:
# conda deactivate
# conda env remove -n job-applier-001

# Create with Python 3.11
conda create -n job-applier-001 python=3.11 -y
conda activate job-applier-001

# Verify version (should show 3.11.x)
python --version

# Install dependencies
pip install -r requirements.txt
```

**Option B: Using venv (alternative)**
```bash
cd apps/api

# Use Python 3.11 specifically
python3.11 -m venv job-applier-001
source job-applier-001/bin/activate  # On Windows: job-applier-001\Scripts\activate

# Verify version
python --version

# Install dependencies
pip install -r requirements.txt
```

### 8. Run the application

**Terminal 1 - API:**
```bash
cd apps/api
conda activate job-applier-001  # or: source job-applier-001/bin/activate if using venv
python -m uvicorn app.main:app --reload
```

**Terminal 2 - Web:**
```bash
cd apps/web
pnpm dev
```

**Terminal 3 - Extension (optional):**
```bash
cd apps/extension
pnpm build
# Then load apps/extension/dist in Chrome
```

## Access Points

- Web app: http://localhost:3000
- API: http://localhost:8000
- API docs: http://localhost:8000/docs

## Troubleshooting

**"pnpm: command not found"**
- Install pnpm: `npm install -g pnpm`

**"workspace:*" errors with npm**
- Use `pnpm`, not `npm`. Install it first.

**MongoDB connection errors**
- Check `MONGODB_URI` in `apps/api/.env`
- Make sure your MongoDB Atlas IP whitelist includes your IP

**Python import errors**
- Make sure conda environment is activated: `conda activate job-applier-001`
- Or if using venv: `source job-applier-001/bin/activate`
- Run `pip install -r requirements.txt` again

**Compilation errors (lxml, pydantic-core)**
- This usually means you're using Python 3.13, which isn't supported yet
- Solution: Recreate environment with Python 3.11:
  ```bash
  conda deactivate
  conda env remove -n job-applier-001
  conda create -n job-applier-001 python=3.11 -y
  conda activate job-applier-001
  pip install -r requirements.txt
  ```
