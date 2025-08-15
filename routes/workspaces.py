from fastapi import APIRouter, Query, HTTPException, Request, Path, Body
from utils.security import validateuser, validateadmin
from models.workspaces import Workspace
from controllers.workspaces import (
    create_workspace,
    get_workspaces,
    get_workspace_by_id,
    update_workspace,
    delete_workspace
)

router = APIRouter(prefix="/workspaces")

@router.post("", tags=["Workspaces"])
@validateuser
async def create_workspace_route(workspace: Workspace, request: Request) -> dict:
    user_id = request.state.id
    result = await create_workspace(workspace, user_id)

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    return result

@router.get("", tags=["Workspaces"])
@validateuser
async def get_workspaces_route(
    request: Request,
    skip: int = Query(default=0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(default=50, ge=1, le=100, description="Número de registros a obtener")
):
    user_id = request.state.id

    result = await get_workspaces(skip=skip, limit=limit, user_id=user_id)

    return result
 

@router.get("{workspace_id}", tags=["Workspaces"])
@validateuser
async def get_workspace_by_id_route(
    workspace_id: str = Path(..., description="ID of the workspace to retrieve"),
    request: Request = None
):
    user_id = request.state.id

    result = await get_workspace_by_id(workspace_id, user_id)

    return result



@router.put("{workspace_id}", tags=["Workspaces"])
@validateuser
async def update_workspace_route(
    workspace_id: str,
    body: dict = Body(...),
    request: Request = None
) -> dict:

    user_id = request.state.id

    result = await update_workspace(workspace_id, user_id, body)

    return result


@router.delete("{workspace_id}", tags=["Workspaces"])
@validateuser
async def delete_workspace_route(
    workspace_id: str = Path(..., description="ID of the workspace to delete"),
    request: Request = None
):
    user_id = request.state.id

    result = await delete_workspace(workspace_id, user_id)

    return result