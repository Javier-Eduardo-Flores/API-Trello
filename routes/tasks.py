from fastapi import APIRouter, HTTPException, Request, Body, Path
from utils.security import validateuser, validateadmin
from models.tasks import Task
from controllers.tasks import (
    create_task,
    get_task_by_id,
    update_task,
    delete_task,
    move_task_to_list
)

router = APIRouter(prefix="/workspaces")


@router.post("/{workspace_id}/lists/{list_id}/tasks", tags=["Tasks"])
@validateuser
async def create_task_route(
    request: Request,
    workspace_id: str,
    list_id: str,
    task_data: Task = Body(...),
):
    user_id = request.state.id
    result = await create_task(task_data, list_id)

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    return result


@router.get("/workspaces/{workspace_id}/lists/{list_id}/tasks/{task_id}", tags=["Tasks"])
@validateuser
async def get_task_route(workspace_id: str, list_id: str, task_id: str, request: Request):
    user_id = request.state.id
    task = await get_task_by_id(task_id, list_id, workspace_id, user_id)
    return {"success": True, "message": "Task retrieved successfully", "data": task}



@router.put("/lists/{list_id}/tasks/{id_task}", tags=["Tasks"])
@validateuser
async def update_task_route(
    list_id: str,
    id_task: str,
    body: dict = Body(...),
    request: Request = None
):
    user_id = request.state.id  
    
    result = await update_task(id_task=id_task, user_id=user_id, list_id=list_id, body=body)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result


@router.delete("/workspaces/{workspace_id}/lists/{list_id}/tasks/{task_id}", tags=["Tasks"])
@validateuser
async def delete_task_route(
    workspace_id: str,
    list_id: str,
    task_id: str,
    request: Request = None
):
    user_id = request.state.id

    result = await delete_task(task_id=task_id, user_id=user_id)

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    return result


@router.put("/{workspace_id}/lists/{list_id}/tasks/{task_id}", tags=["Tasks"])
@validateuser
async def move_task_to_list_route(
    workspace_id: str,
    list_id: str,
    task_id: str,
    new_list_id: str,
    request: Request
):
    user_id = request.state.id
    result = await move_task_to_list(task_id, new_list_id, user_id)

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    return result
