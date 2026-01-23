# Installation Guide 🔧

👈 **[Back to main README](README.md)**

Complete step-by-step instructions to get JobCopilot running on your local machine.

## 🛠️ Prerequisites

### Required Software
- **Python 3.11+** (3.12 recommended)
- **Node.js 18+** with npm
- **Git** for cloning the repository
- **Conda** (recommended) or pip for Python environment management

### Free Accounts Needed
- **MongoDB Atlas** (cloud database)
- **OpenAI Platform** (for AI features)

## 🚀 Quick Setup (5 minutes)

```bash
# 1. Clone and enter directory
git clone https://github.com/DKethan/job-applier-001.git
cd job-applier-001

# 2. Set up Python environment
conda create -n jobcopilot python=3.11 -y
conda activate jobcopilot

# 3. Install backend dependencies
cd apps/api
pip install -r requirements.txt

# 4. Install frontend dependencies (new terminal)
cd ../..
npm install -g pnpm  # or use npm
pnpm install

# 5. Get API keys and configure (see detailed steps below)

# 6. Start services
# Terminal 1: Backend
cd apps/api
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
pnpm run dev

# 7. Open http://localhost:3000
```

## 📋 Detailed Installation Steps

### Step 1: Clone the Repository

```bash
git clone https://github.com/DKethan/job-applier-001.git
cd job-applier-001
```

### Step 2: Set Up Python Environment

#### Option A: Using Conda (Recommended)

```bash
# Create isolated environment
conda create -n jobcopilot python=3.11 -y
conda activate jobcopilot

# Verify Python version
python --version  # Should show Python 3.11.x
```

#### Option B: Using venv (Alternative)

```bash
# Create virtual environment
python -m venv jobcopilot-env

# Activate environment
# On macOS/Linux:
source jobcopilot-env/bin/activate
# On Windows:
jobcopilot-env\Scripts\activate

# Upgrade pip
pip install --upgrade pip
```

### Step 3: Get Your API Keys

#### MongoDB Atlas Setup

1. **Create Account**
   - Visit [MongoDB Atlas](https://www.mongodb.com/atlas)
   - Click "Start free" and create your account

2. **Create Database Cluster**
   - Choose the "FREE" tier
   - Select your preferred cloud provider and region
   - Click "Create Cluster"
   - Wait 5-10 minutes for setup

3. **Get Connection String**
   - Go to "Database" → "Connect"
   - Choose "Connect your application"
   - Select "Python" driver, version "3.6 or later"
   - Copy the connection string
   - **Format**: `mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority`

#### OpenAI API Setup

1. **Create Account**
   - Visit [OpenAI Platform](https://platform.openai.com/)
   - Create account or sign in

2. **Generate API Key**
   - Go to "API Keys" section
   - Click "Create new secret key"
   - Give it a name like "JobCopilot"
   - **Copy the key immediately** (starts with `sk-`)
   - **Important**: Save this securely - you can't see it again!

3. **Check Credits**
   - New accounts get $5 in free credits
   - GPT-4o-mini costs ~$0.0015 per 1K tokens
   - Should last for hundreds of resume tailorings

### Step 4: Configure Environment Variables

```bash
# Copy example configuration files
cp .env.example .env
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.example apps/web/.env
```

#### Edit `apps/api/.env`

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-your-actual-openai-key-here
OPENAI_MODEL=gpt-4o-mini

# MongoDB Configuration
MONGODB_URI=mongodb+srv://your-username:your-password@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
MONGODB_DB_NAME=jobcopilot

# Security Keys (generate these)
ENCRYPTION_KEY=your-32-character-encryption-key
JWT_SECRET_KEY=your-jwt-secret-key

# Storage
STORAGE_LOCAL_DIR=./data/uploads
```

#### Generate Security Keys

```bash
# Run the key generation script
python3 scripts/generate_secrets.py
```

Copy the generated keys into your `.env` file.

#### Edit `apps/web/.env.local`

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Step 5: Install Backend Dependencies

```bash
# Navigate to backend directory
cd apps/api

# Install Python packages
pip install -r requirements.txt
```

**Common Issues:**
- If you get permission errors, try: `pip install --user -r requirements.txt`
- For Apple Silicon Macs, you might need: `pip install --no-cache-dir -r requirements.txt`

### Step 6: Install Frontend Dependencies

```bash
# Go back to project root
cd ../..

# Install pnpm globally (optional but recommended)
npm install -g pnpm

# Install dependencies
pnpm install
# or if using npm:
# npm install
```

### Step 7: Start the Development Servers

#### Terminal 1: Backend Server

```bash
# Navigate to backend
cd apps/api

# Start FastAPI server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Success indicators:**
```
INFO:     Will watch for changes in these directories: ['...']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

#### Terminal 2: Frontend Server

```bash
# In project root (separate terminal)
pnpm run dev
# or npm run dev
```

**Success indicators:**
```
✓ Ready - started server on http://localhost:3000
event - compiled client and server successfully
```

### Step 8: Test the Installation

1. **Open Browser**: Go to http://localhost:3000
2. **Create Account**: Sign up with email/password
3. **Upload Resume**: Try uploading a PDF or DOCX resume
4. **Test Tailoring**: Paste a job posting URL and try the tailoring feature

## 🔧 Troubleshooting

### Backend Won't Start

**Port 8000 already in use:**
```bash
# Kill process using port 8000
lsof -ti:8000 | xargs kill -9
# or use a different port
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

**MongoDB connection failed:**
- Check your connection string in `.env`
- Make sure MongoDB Atlas IP whitelist includes your IP (0.0.0.0/0 for testing)
- Verify username/password in connection string

**OpenAI API errors:**
- Check your API key is correct
- Verify you have credits remaining
- Test with a simple curl command

### Frontend Won't Start

**Node version issues:**
```bash
# Check Node version
node --version  # Should be 18+
npm --version   # Should be 8+
```

**Port 3000 conflicts:**
```bash
# Use different port
pnpm run dev -- -p 3001
```

### Database Issues

**Indexes not created:**
- The app automatically creates indexes on first run
- Check MongoDB Atlas dashboard for database creation

**Connection timeouts:**
- Check network connectivity
- Verify MongoDB Atlas cluster is awake (free tier sleeps after inactivity)

### Common Errors

**ModuleNotFoundError:**
```bash
# Reinstall dependencies
cd apps/api && pip install -r requirements.txt --force-reinstall
```

**Template errors:**
- Make sure all required template files exist in `apps/api/app/templates/`

## 🌐 Production Deployment

### Using Docker (Recommended)

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Check logs
docker-compose logs -f
```

### Manual Production Setup

1. **Set production environment variables**
2. **Use a production WSGI server** (like Gunicorn)
3. **Set up reverse proxy** (nginx)
4. **Configure SSL certificates**
5. **Set up monitoring and logging**

## 📞 Support

- **GitHub Issues**: [Report bugs](https://github.com/DKethan/job-applier-001/issues)
- **API Documentation**: http://localhost:8000/docs (when running)
- **Community**: Join our discussions for help

## 🔄 Updating JobCopilot

```bash
# Pull latest changes
git pull origin main

# Update dependencies
cd apps/api && pip install -r requirements.txt --upgrade
cd ../.. && pnpm update

# Restart servers
# Backend: Ctrl+C then restart uvicorn
# Frontend: Should auto-reload
```

---

*Installation complete? Check out [current features](README-CURRENT.md) to start using JobCopilot!* 🎉