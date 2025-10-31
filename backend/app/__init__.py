from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api import ai, tweets

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered platform for analyzing, planning, and automatically creating viral posts on X (Twitter)",
    version="1.0.0",
)

# CORS middleware
# WARNING: CORS allows all origins - restrict to specific domains in production!
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ai.router, prefix="/api/ai", tags=["AI"])
app.include_router(tweets.router, prefix="/api/tweets", tags=["Tweets"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "X Post Automation API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}
