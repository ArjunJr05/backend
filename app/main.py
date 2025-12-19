from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
from dotenv import load_dotenv
from app.api import submit, status, leaderboard, auth, test_auth
from app.db.firebase_service import init_firebase
from app.core.worker import start_worker, stop_worker
from app.config import ALLOWED_ORIGINS

# Load environment variables from .env file
load_dotenv()

worker = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_firebase()
    global worker
    worker = await start_worker()
    yield
    await stop_worker()

app = FastAPI(
    title="ML Hackathon Evaluation Platform",
    description="Backend API for ML model evaluation and leaderboard",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(test_auth.router, tags=["Testing"])
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(submit.router, tags=["Submission"])
app.include_router(status.router, tags=["Status"])
app.include_router(leaderboard.router, tags=["Leaderboard"])

@app.get("/")
async def root():
    return {
        "message": "ML Hackathon Evaluation Platform API",
        "version": "1.0.0",
        "endpoints": {
            "submit": "/submit-endpoint",
            "queue_status": "/queue-status/{team_id}",
            "leaderboard": "/leaderboard",
            "team_result": "/team-result/{team_id}"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
