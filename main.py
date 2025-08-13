import uvicorn 
import logging

from fastapi import FastAPI ,requests
from controllers.users import create_user ,login

from models.users import User
from models.login import Login

from routes.workspaces import router as workspaces_router
from routes.tasks import router as tasks_router
from routes.lists import router as lists_router

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app.include_router(workspaces_router)
app.include_router(tasks_router)
app.include_router(lists_router)
@app.get("/")
def read_root():
    return {"message": "Welcome to the Trello Clone API"}

@app.post("/users")
async def register_user(user: User) -> User:
    """
    Endpoint to register a new user
    """
    return await create_user(user)


@app.post("/login")
async def login_access(l: Login) -> dict:
    return await login(l)