from models.tasks import Task
from utils.mongodb import get_collection
from fastapi import HTTPException
from bson import ObjectId
from pipelines.task_pipline import get_task_by_title_in_workspace_pipeline, get_tasks_by_workspace_pipeline
tasks_collection = get_collection("tasks")
lists_collection = get_collection("lists")
workspaces_collection = get_collection("workspaces")


async def create_task(user_id:str,id_workspace: str, task: Task, id_list: str) -> dict:
    try:
        workspace =  workspaces_collection.find_one({"_id": ObjectId(id_workspace)})
        if not workspace:
            return {"success": False, "message": "Workspace not found", "data": None}
        if workspace["id_user"] != user_id:
            return {"success": False, "message": "Unauthorized", "data": None}

        list_data = lists_collection.find_one({"_id": ObjectId(id_list), "id_workspace": id_workspace})
        if not list_data:
            return {"success": False, "message": "List not found in workspace", "data": None}
        normalized_title = task.title.strip().lower()


        existing_task = tasks_collection.aggregate(
            get_task_by_title_in_workspace_pipeline(id_workspace, normalized_title)
        )
        existing_task = list(existing_task)

        if existing_task:
            return {"success": False, "message": "Task already exists", "data": None}

        task_dict = task.model_dump(exclude={"id"})
        task_dict["id_list"] = id_list

        inserted =  tasks_collection.insert_one(task_dict)
        
# A considerar agregar las fechas de creacion y actualizacion

        response_data = {
            "id": str(inserted.inserted_id),
            "title": task.title,
            "description": task.description,
            "id_list": id_list, 
        }
        return {"success": True, "message": "Task created successfully", "data": response_data}

    except Exception as e:
        return {"success": False, "message": str(e), "data": None}

#------------------------------------------------------------------------------------
async def get_task_by_id(task_id: str, workspace_id: str) -> Task:
    try:
        workspace =  workspaces_collection.find_one({"_id": ObjectId(workspace_id)})
        if not workspace:
            raise HTTPException(status_code=404, detail="Workspace not found")

        task =  tasks_collection.find_one({"_id": ObjectId(task_id)})
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

       
        list_data =  lists_collection.find_one({
            "_id": ObjectId(task["id_list"]),
            "id_workspace": workspace_id 
        })

        if not list_data:
            raise HTTPException(status_code=404, detail="List not found or does not belong to workspace")

        
        return Task(
            id=str(task["_id"]),
            title=task["title"],
            description=task.get("description", ""),
            id_list=task["id_list"],
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching task: {str(e)}")


#-------------------------------------------------------------------------------------------

async def get_tasks_by_workspace(workspace_id: str) -> list:
    try:
        workspace = workspaces_collection.find_one({"_id": ObjectId(workspace_id)})
        if not workspace:
            return {"success": False, "message": "Workspace not found", "data": None}

        pipeline = get_tasks_by_workspace_pipeline(workspace_id)
        tasks_with_lists = tasks_collection.aggregate(pipeline)

        tasks_with_lists = list(tasks_with_lists)

        return {"success": True, "message": "Tasks retrieved successfully", "data": tasks_with_lists}

    except Exception as e:
        return {"success": False, "message": str(e), "data": None}

#------------------------------------------------------------------------------------

async def update_task(user_id: str, id_task: str, workspace_id: str,  task_data: Task) -> dict:
    try:
       
        task =  tasks_collection.find_one({"_id": ObjectId(id_task)})
        if not task:
            return {"success": False, "message": "Task not found", "data": None}
     
        workspace =  workspaces_collection.find_one({"_id": ObjectId(workspace_id)})
        if not workspace_id:
            return {"success": False, "message": "Workspace ID not found in list", "data": None}

        list_data = get_list_by_id(ObjectId(task["id_list"]), workspace_id)
        if not list_data:
            return {"success": False, "message": "List not found", "data": None}

        if workspace["id_user"] != user_id:
            return {"success": False, "message": "Unauthorized", "data": None}

        if not task_data.description:
            task_data.description = task["description"]
        if not task_data.title:
            task_data.title = task["title"]

        title_new = task_data.title.strip()
        description_new = task_data.description.strip()

        title_old = task["title"]
        description_old = task["description"]
        
        if title_new == title_old and description_new == description_old:
            return {"success": False, "message": "No changes made to the task", "data": None}

        existing_task = tasks_collection.aggregate(
            get_task_by_title_in_workspace_pipeline(workspace_id, task_data.title.strip())
        )
        existing_task = list(existing_task)

        if description_new == description_old:
            if existing_task:
                return {"success": False, "message": "Task with this title already exists in the workspace", "data": None}

        new_task = task_data.model_dump(exclude={"id"})
        new_task["id_list"] = task["id_list"]
        result =  tasks_collection.update_one(
            {"_id": ObjectId(id_task)},
            {"$set": new_task}
        )

        response_data = {
            "id": id_task,
            "title": new_task["title"],
            "description": new_task["description"],
            "id_list": new_task["id_list"]
        }

        return {"success": True, "message": "Task updated successfully", "data": response_data}

    except Exception as e:
        return {"success": False, "message": str(e), "data": None}

#------------------------------------------------------------------------------------

async def delete_task(task_id: str, user_id: str) -> dict:
    try:
        task =  tasks_collection.find_one({"_id": ObjectId(task_id)})
        if not task:
            return {"success": False, "message": "Task not found", "data": None}

        list_id = task.get("id_list")
        if not list_id:
            return {"success": False, "message": "List ID not found in task", "data": None}

        list_data =  lists_collection.find_one({"_id": ObjectId(list_id)})
        if not list_data:
            return {"success": False, "message": "List not found", "data": None}

        workspace_id = list_data.get("id_workspace")
        if not workspace_id:
            return {"success": False, "message": "Workspace ID not found in list", "data": None}

        workspace =  workspaces_collection.find_one({"_id": ObjectId(workspace_id)})
        if not workspace:
            return {"success": False, "message": "Workspace not found", "data": None}

        if str(workspace.get("id_user")) != user_id:
            return {"success": False, "message": "Unauthorized", "data": None}

        tasks_collection.delete_one({"_id": ObjectId(task_id)})

        task_delete.model_dump()
        return {"success": True, "message": "Task deleted successfully", "data": None}

    except Exception as e:
        return {"success": False, "message": str(e), "data": None}

#------------------------------------------------------------------------------------

async def move_task_to_list(workspace_id: str, task_id: str, new_list_id: str) -> dict:
    try:
        task = tasks_collection.find_one({"_id": ObjectId(task_id)})
        if not task:
            return {"success": False, "message": "Task not found", "data": None}

        current_list_id = task.get("id_list")
        if not current_list_id:
            return {"success": False, "message": "Task has no associated list", "data": None}

        current_list = lists_collection.find_one({"_id": ObjectId(current_list_id)})
        new_list = lists_collection.find_one({"_id": ObjectId(new_list_id)})

        if not current_list or not new_list:
            return {"success": False, "message": "One or both lists not found", "data": None}

        
        if str(current_list.get("id_workspace")) != workspace_id or str(new_list.get("id_workspace")) != workspace_id:
            return {"success": False, "message": "Lists are not in the given workspace", "data": None}

        
        tasks_collection.update_one(
            {"_id": ObjectId(task_id)},
            {"$set": {"id_list": new_list_id}}
        )

        return {
            "success": True,
            "message": "Task moved successfully",
            "data": {
                "task_id": task_id,
                "new_list_id": new_list_id
            }
        }
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}

