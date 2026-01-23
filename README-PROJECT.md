# Technical Documentation 💻

👈 **[Back to main README](README.md)**

## 🏗️ How JobCopilot Works Behind the Scenes

Hey developers! Want to understand how JobCopilot ticks? Here's the friendly overview of our tech stack and architecture.

### Tech Stack Overview

**Frontend (What You Interact With)**
- Next.js + React for a smooth, modern web experience
- TypeScript for reliable, bug-free code
- Tailwind CSS for beautiful, responsive design
- Works perfectly on desktop, tablet, and mobile

**Backend (The Smart Engine)**
- FastAPI (Python) for super-fast API responses
- GPT-4o-mini integration for AI-powered content creation
- Smart document processing and file handling
- Secure user authentication and data management

**Data & Infrastructure**
- MongoDB for flexible, secure data storage
- Encrypted file storage for your documents
- Modern security practices (HTTPS, encryption, etc.)
- Docker-ready for easy deployment

## 📁 Project Layout (Simplified)

```
job-applier-001/
├── apps/                    # Main Applications
│   ├── api/                 # Backend (Python/FastAPI)
│   ├── web/                 # Frontend (Next.js/React)
│   └── extension/           # Chrome Extension
├── packages/shared/         # Shared Code
├── scripts/                 # Helper Scripts
├── data/                    # File Storage
└── README files             # Documentation
```

**Key Folders:**
- `apps/api/` - Server-side logic, AI processing, database
- `apps/web/` - User interface and web pages
- `apps/extension/` - Browser automation tools
- `packages/shared/` - Code shared between apps

## 🔌 API Overview

### Quick API Info
- **Base URL**: `http://localhost:8000/v1`
- **Authentication**: JWT tokens (except signup/login)
- **Format**: JSON requests/responses
- **Full docs**: Visit `http://localhost:8000/docs` when running

### Main API Groups

**👤 Account Management**
- User registration, login, profile updates
- Secure authentication with JWT tokens

**📄 Resume & Profile**
- Upload and parse resumes (PDF/DOCX)
- Edit and manage your professional profile
- Store work experience, skills, education

**🔍 Job Processing**
- Paste job URLs and analyze requirements
- Extract key information from job postings
- Support for major job boards and ATS systems

**🤖 AI Tailoring**
- Customize resumes for specific jobs
- Generate personalized cover letters
- Choose from professional templates

**📥 Downloads**
- Secure file downloads
- ZIP packages with resume + cover letter
- Organized and ready-to-use documents

### Response Format
```json
{
  "success": true,
  "data": { "your": "data" },
  "message": "Optional success message"
}
```

## 🗄️ Data Storage

### What We Store

**User Accounts**
- Login credentials and basic profile info
- Account settings and preferences

**Professional Profiles**
- Work experience, education, skills
- Uploaded resume files and parsed data
- Custom edits and profile updates

**Job Applications**
- Job posting details and analysis
- Tailored documents and templates used
- Application history and status

**Files & Documents**
- Secure storage of generated resumes/cover letters
- File metadata and access controls
- Download history and permissions

**All data is encrypted and securely stored in MongoDB Atlas.**


## 🔧 Development Setup

**📖 For detailed installation steps, check out [README-INSTALL.md](README-INSTALL.md)**

### Quick Start for Developers
- Python 3.11+, Node.js 18+, MongoDB Atlas, OpenAI API key
- Follow the installation guide for complete setup
- Backend runs on `http://localhost:8000` (with auto-reload)
- Frontend runs on `http://localhost:3000`

### Local Development

```bash
# Clone repository
git clone https://github.com/DKethan/job-applier-001.git
cd job-applier-001

# Set up Python environment
conda create -n jobcopilot python=3.11 -y
conda activate jobcopilot

# Install backend dependencies
cd apps/api
pip install -r requirements.txt

# Install frontend dependencies
cd ../..
pnpm install

# Configure environment variables
cp apps/api/.env.example apps/api/.env
# Edit .env with your API keys

# Start backend (terminal 1)
cd apps/api
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Start frontend (terminal 2)
pnpm run dev
```

### Testing

```bash
# Backend tests
cd apps/api
python -m pytest

# Frontend tests
cd apps/web
pnpm test

# End-to-end tests (future)
pnpm test:e2e
```

### Code Quality

```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Run linting
cd apps/web && pnpm run lint
cd apps/api && flake8

# Type checking
cd apps/web && pnpm run type-check
```

## 🔒 Security

### Data Protection
- **Encryption**: Sensitive data encrypted using Fernet
- **JWT Tokens**: Secure authentication with expiration
- **Input Validation**: All inputs validated and sanitized
- **Rate Limiting**: API rate limiting to prevent abuse

### File Security
- **Access Control**: Files accessible only to owners
- **Secure URLs**: Time-limited download URLs
- **Virus Scanning**: Future implementation for uploaded files
- **Storage Encryption**: Files encrypted at rest

### API Security
- **CORS**: Configured for allowed origins
- **HTTPS**: Required in production
- **API Keys**: Secure key management for external services
- **Audit Logging**: All API calls logged for security monitoring

## 📊 Monitoring & Logging

### Application Logs
- **Structured Logging**: JSON format with correlation IDs
- **Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Log Rotation**: Automatic log rotation and cleanup
- **Centralized Logging**: Future implementation

### Performance Monitoring
- **Response Times**: API endpoint performance tracking
- **Error Rates**: Automatic error detection and alerting
- **Resource Usage**: CPU, memory, and disk monitoring
- **User Analytics**: Usage patterns and feature adoption

### Health Checks
```
GET /health  # Overall system health
GET /health/db  # Database connectivity
GET /health/ai  # AI service availability
```

## 🚀 Deployment

### Development
- **Local Environment**: Docker Compose for consistent setup
- **Hot Reload**: Automatic code reloading during development
- **Debug Tools**: Integrated debugging and profiling tools

### Production
- **Containerization**: Docker images for all services
- **Orchestration**: Kubernetes for scaling and management
- **Load Balancing**: Nginx reverse proxy with SSL termination
- **CDN**: Static asset delivery optimization

### Environment Variables

#### Backend (.env)
```bash
# Required
OPENAI_API_KEY=sk-...
MONGODB_URI=mongodb+srv://...
ENCRYPTION_KEY=32_char_key
JWT_SECRET_KEY=jwt_secret

# Optional
OPENAI_MODEL=gpt-4o-mini
MONGODB_DB_NAME=jobcopilot
STORAGE_LOCAL_DIR=./data/uploads
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=8000
```

#### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_ENVIRONMENT=development
```

## 🤝 Contributing

### Development Workflow
1. **Fork & Clone**: Create your own fork of the repository
2. **Branch**: Create feature branch from `main`
3. **Develop**: Write code and tests
4. **Test**: Run full test suite
5. **Commit**: Follow conventional commit format
6. **PR**: Create pull request with description

### Code Standards
- **Python**: PEP 8 with Black formatting
- **TypeScript**: ESLint with Prettier
- **Documentation**: Clear docstrings and comments
- **Testing**: Minimum 80% code coverage

### Areas for Contribution
- **Frontend**: UI/UX improvements, new features
- **Backend**: API enhancements, performance optimization
- **AI/ML**: Better tailoring algorithms, new models
- **DevOps**: Infrastructure, deployment, monitoring
- **Documentation**: Guides, tutorials, API docs

### Need Help?
- **GitHub Issues**: Perfect for bugs and feature requests
- **Community**: Friendly developers ready to help
- **Documentation**: Check our guides first!

---

*Ready to contribute? Check our [installation guide](README-INSTALL.md) for getting started!* 🚀