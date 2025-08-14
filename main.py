import uvicorn 
import logging

from fastapi import FastAPI ,requests
from controllers.users import create_user ,login

from models.users import User
from models.login import Login

from routes.workspaces import router as workspaces_router
from routes.tasks import router as tasks_router
from routes.lists import router as lists_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app.include_router(workspaces_router)
app.include_router(tasks_router)
app.include_router(lists_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Trello Clone API"}

@app.get("/health")
def health_check():
    try:
        return {
            "status": "healthy",
            "timestamp": "2025-08-15",
            "service": "Trello Clone API",
            "environment": "production"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@app.get("/ready")
def readiness_check():
    try:
        from utils.mongodb import get_collection
        db_status = test_connection()

        return {"status": "ready" if db_status else "not ready",
                "database":"connected" if db_status else "not connected",
                "service": "Trello Clone API"
               }
    except Exception as e:
        return {"status": "not ready", "error": str(e)}




@app.post("/users")
async def register_user(user: User) -> User:
    """
    Endpoint to register a new user
    """
    return await create_user(user)


@app.post("/login")
async def login_access(l: Login) -> dict:
    return await login(l)