from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.utils.app_logger import app_logger
from app.database import init_db

# Initialize database
init_db()

app = FastAPI(
    title="JobCopilot API",
    description="AI Job Application Copilot API",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health():
    return {"status": "healthy"}


# Import routers
from app.routers import auth, profile, jobs, tailor, extension, downloads

app.include_router(auth.router, prefix="/v1/auth", tags=["auth"])
app.include_router(profile.router, prefix="/v1/profile", tags=["profile"])
app.include_router(jobs.router, prefix="/v1/jobs", tags=["jobs"])
app.include_router(tailor.router, prefix="/v1/tailor", tags=["tailor"])
app.include_router(extension.router, prefix="/v1/extension", tags=["extension"])
app.include_router(downloads.router, prefix="/v1/downloads", tags=["downloads"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.api_host, port=settings.api_port)
