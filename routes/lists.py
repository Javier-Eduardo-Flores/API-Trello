from fastapi import APIRouter, HTTPException, Request
from utils.security import validateuser, validateadmin
from models.list import List
from controllers.lists import (
    create_list,
    get_lists,
    update_list,
    delete_list
)

router = APIRouter(prefix="/workspaces")

@router.post("/{workspace_id}/lists", tags=["Lists"])
@validateuser
async def create_list_route(
    workspace_id: str = Path(..., description="ID of the workspace"),
    list_data: List = Body(...),
    request: Request = None
):
    user_id = request.state.id
    result = await create_list(list_data, workspace_id, user_id)

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    return result


@router.get("/{workspace_id}/lists", tags=["Lists"])
@validateuser
async def get_lists_route(workspace_id: str, request: Request):
    user_id = request.state.id 

    result = await get_lists(workspace_id=workspace_id, user_id=user_id)

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    return result


@router.put("/{workspace_id}/lists/{list_id}", tags=["Lists"])
@validateuser
async def update_list_route(
    workspace_id: str,
    list_id: str,
    request: Request,
    body: dict = Body(...)
):

    user_id = request.state.id

    result = await update_list(list_id=list_id, user_id=user_id, body=body)

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    return result



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