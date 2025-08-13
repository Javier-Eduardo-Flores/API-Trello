from fastapi import APIRouter, HTTPException, Request, Query, Path
from utils.security import validateuser, validateadmin
from models.tasks import Task
from controllers.tasks import (
    create_task,
    get_task_by_id,
    update_task,
    delete_task,
    move_task_to_list,
    get_tasks_by_workspace
)

router = APIRouter(prefix="/workspaces")


@router.post("/{workspace_id}/lists/{list_id}/tasks", tags=["Tasks"])
@validateuser
async def create_task_route(
    request: Request,
    workspace_id: str,
    list_id: str,
    task_data: Task,
):
    user_id = request.state.id
    result = await create_task(user_id, workspace_id, task_data, list_id)

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    return result

#------------------------------------------------------------------------------------------

@router.get("/{workspace_id}/tasks/{task_id}", tags=["Tasks"])
@validateuser
async def get_task_route(workspace_id: str, task_id: str, request: Request):

    task = await get_task_by_id(task_id,workspace_id)
    return {"success": True, "message": "Task retrieved successfully", "data": task}

#-----------------------------------------------------------------------------------------------

@router.get("/{workspace_id}/tasks", tags=["Tasks"])
@validateuser
async def get_task_route(request: Request, workspace_id: str):
    result = await get_tasks_by_workspace(workspace_id)

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result

#---------------------------------------------------------------------------------------------

@router.put("/{workspace_id}/tasks/{id_task}", tags=["Tasks"])
@validateuser
async def update_task_route(
    id_task: str,
    workspace_id: str,
    task : Task,
    request: Request
):
    user_id = request.state.id  
    
    result = await update_task(user_id, id_task, workspace_id, task)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

#-------------------------------------------------------------------------------------------------

@router.delete("/{workspace_id}/tasks/{task_id}", tags=["Tasks"])
@validateuser
async def delete_task_route(
    workspace_id: str,
    task_id: str,
    request: Request 
):
    user_id = request.state.id

    result = await delete_task(task_id,user_id)

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    return result

#----------------------------------------------------------------------------------------------

@router.put("/{workspace_id}/tasks/{task_id}/move", tags=["Tasks"])
@validateuser
async def move_task_route(
    request: Request,
    workspace_id: str,
    task_id: str,
    new_list_id: str = Query(..., description="ID de la nueva lista"),
):
    result = await move_task_to_list(workspace_id, task_id, new_list_id)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result
