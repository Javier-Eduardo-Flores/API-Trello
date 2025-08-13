from fastapi import APIRouter, HTTPException, Request
from utils.security import validateuser, validateadmin
from models.lists import List
from controllers.lists import (
    create_list,
    get_lists,
    update_list,
    delete_list,
    get_list_by_id
) 

router = APIRouter(prefix="/workspaces")

@router.post("/{workspace_id}/lists", tags=["Lists"])
@validateuser
async def create_list_route(
    workspace_id: str,
    list_data: List,
    request: Request
):
    user_id = request.state.id
    result = await create_list(list_data, workspace_id, user_id)

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    return result

# ----------------------------------------------------------------------------------

@router.get("/{workspace_id}/lists", tags=["Lists"])
@validateuser
async def get_lists_route(workspace_id: str, request: Request):
    user_id = request.state.id 

    result = await get_lists(workspace_id)

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    return result

# ----------------------------------------------------------------------------------

@ router.get("/{workspace_id}/lists/{list_id}", tags=["Lists"])
@validateuser
async def get_list_by_id_route(
    workspace_id: str,
    list_id: str,
    request: Request
):
    user_id = request.state.id

    result = await get_list_by_id(list_id=list_id, workspace_id=workspace_id)

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    return result

# ----------------------------------------------------------------------------------

@router.put("/{workspace_id}/lists/{list_id}", tags=["Lists"])
@validateuser
async def update_list_route(
    workspace_id: str,
    list_id: str,
    list_data: List,
    request: Request 
):

    user_id = request.state.id

    result = await update_list(list_id=list_id, user_id=user_id, list_data=list_data)

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    return result

# ----------------------------------------------------------------------------------

@router.delete("/{workspace_id}/lists/{list_id}", tags=["Lists"])
@validateuser
async def delete_list_route(
    workspace_id: str,
    list_id: str,
    request: Request
):

    user_id = request.state.id

    result = await delete_list(list_id=list_id, user_id=user_id)

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    return result