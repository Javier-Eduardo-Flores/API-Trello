from fastapi import APIRouter, HTTPException, Request, Query, Path, Depends
from utils.security import validateuser, validateadmin
from utils.mongodb import get_tasks_collection, get_lists_collection, get_workspaces_collection
from models.tasks import Task
from controllers.tasks import (
    create_task,
    get_task_by_id,
    update_task,
    delete_task,
    move_task_to_list,
    get_tasks_by_workspace
)
from pymongo.collection import Collection

router = APIRouter(prefix="/workspaces")


@router.post("/{workspace_id}/lists/{list_id}/tasks", tags=["Tasks"])
@validateuser
async def create_task_route(
    request: Request,
    workspace_id: str,
    list_id: str,
    task_data: Task,
    tasks_collection: Collection = Depends(get_tasks_collection),
    lists_collection: Collection = Depends(get_lists_collection),
    workspaces_collection: Collection = Depends(get_workspaces_collection)
):
    user_id = request.state.id
    result = await create_task(user_id, workspace_id, task_data, list_id, tasks_collection, lists_collection, workspaces_collection)

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    return result


@router.get("/{workspace_id}/tasks/{task_id}", tags=["Tasks"])
@validateuser
async def get_task_route(workspace_id: str, task_id: str, request: Request,
    tasks_collection: Collection = Depends(get_tasks_collection),
    lists_collection: Collection = Depends(get_lists_collection),
    workspaces_collection: Collection = Depends(get_workspaces_collection)):

    task = await get_task_by_id(task_id, workspace_id, tasks_collection, lists_collection, workspaces_collection)
    return {"success": True, "message": "Task retrieved successfully", "data": task}


@router.get("/{workspace_id}/tasks", tags=["Tasks"])
@validateuser
async def get_tasks_route(request: Request, workspace_id: str,
    tasks_collection: Collection = Depends(get_tasks_collection),
    workspaces_collection: Collection = Depends(get_workspaces_collection)):
    result = await get_tasks_by_workspace(workspace_id, tasks_collection, workspaces_collection)

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@router.put("/{workspace_id}/tasks/{id_task}", tags=["Tasks"])
@validateuser
async def update_task_route(
    id_task: str,
    workspace_id: str,
    task: Task,
    request: Request,
    tasks_collection: Collection = Depends(get_tasks_collection),
    lists_collection: Collection = Depends(get_lists_collection),
    workspaces_collection: Collection = Depends(get_workspaces_collection)
):
    user_id = request.state.id

    result = await update_task(user_id, id_task, workspace_id, task, tasks_collection, lists_collection, workspaces_collection)

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    return result


@router.delete("/{workspace_id}/tasks/{task_id}", tags=["Tasks"])
@validateuser
async def delete_task_route(
    workspace_id: str,
    task_id: str,
    request: Request,
    tasks_collection: Collection = Depends(get_tasks_collection),
    lists_collection: Collection = Depends(get_lists_collection),
    workspaces_collection: Collection = Depends(get_workspaces_collection)
):
    user_id = request.state.id

    result = await delete_task(task_id, user_id, tasks_collection, lists_collection, workspaces_collection)

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    return result


@router.put("/{workspace_id}/tasks/{task_id}/move", tags=["Tasks"])
@validateuser
async def move_task_route(
    request: Request,
    workspace_id: str,
    task_id: str,
    new_list_id: str = Query(..., description="ID de la nueva lista"),
    tasks_collection: Collection = Depends(get_tasks_collection),
    lists_collection: Collection = Depends(get_lists_collection)
):
    result = await move_task_to_list(workspace_id, task_id, new_list_id, tasks_collection, lists_collection)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result
