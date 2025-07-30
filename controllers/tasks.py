from models.tasks import Task
from utils.mongodb import get_collection
from fastapi import HTTPException
from bson import ObjectId

tasks_collection = get_collection("tasks")
lists_collection = get_collection("lists")
workspaces_collection = get_collection("workspaces")

async def create_task(task: Task, id_list: str) -> dict:
    try:
        normalized_title = task.title.strip().lower()

        existing_task = await tasks_collection.find_one({
            "$expr": {
                "$eq": [
                    {"$toLower": "$title"},
                    normalized_title
                ]
            },
            "id_list": id_list
        })

        if existing_task:
            return {"success": False, "message": "Task already exists", "data": None}

        task_dict = task.model_dump(exclude={"id"})
        task_dict["id_list"] = id_list

        inserted = await tasks_collection.insert_one(task_dict)
        task_dict["id"] = str(inserted.inserted_id)

        return {"success": True, "message": "Task created successfully", "data": task_dict}

    except Exception as e:
        return {"success": False, "message": str(e), "data": None}

#------------------------------------------------------------------------------------

async def get_task_by_id(task_id: str, list_id: str, workspace_id: str, user_id: str) -> Task:
    try:
       
        workspace = await workspaces_collection.find_one({"_id": ObjectId(workspace_id)})
        if not workspace:
            raise HTTPException(status_code=404, detail="Workspace not found")

        if str(workspace.get("id_user")) != user_id:
            raise HTTPException(status_code=403, detail="Unauthorized")

        
        list_doc = await lists_collection.find_one({"_id": ObjectId(list_id), "id_workspace": workspace_id})
        if not list_doc:
            raise HTTPException(status_code=404, detail="List not found in workspace")

        
        task_doc = await tasks_collection.find_one({"_id": ObjectId(task_id), "id_list": list_id})
        if not task_doc:
            raise HTTPException(status_code=404, detail="Task not found in list")

        
        task_doc["id"] = str(task_doc["_id"])
        del task_doc["_id"]

        return Task(**task_doc)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching task: {str(e)}")


#------------------------------------------------------------------------------------
async def update_task(id_task: str, user_id: str, list_id: str, body: dict) -> dict:
    try:
       
        task = await tasks_collection.find_one({"_id": ObjectId(id_task)})
        if not task:
            return {"success": False, "message": "Task not found", "data": None}

        
        list_data = await lists_collection.find_one({"_id": ObjectId(list_id)})
        if not list_data:
            return {"success": False, "message": "List not found", "data": None}

        
        workspace_id = list_data.get("id_workspace")
        if not workspace_id:
            return {"success": False, "message": "Workspace ID not found in list", "data": None}

       
        workspace = await workspaces_collection.find_one({"_id": ObjectId(workspace_id)})
        if not workspace:
            return {"success": False, "message": "Workspace not found", "data": None}

        
        if str(workspace.get("id_user")) != user_id:
            return {"success": False, "message": "Unauthorized", "data": None}

    
        if "title" in body:
            normalized_title = body["title"].strip().lower()
            existing_task = await tasks_collection.find_one({
                "$expr": {
                    "$eq": [
                        {"$toLower": "$title"},
                        normalized_title
                    ]
                },
                "id_list": list_id,
                "_id": {"$ne": ObjectId(id_task)}
            })
            if existing_task:
                return {"success": False, "message": "Task with this title already exists in the list", "data": None}

        if not body:
            return {"success": False, "message": "No fields to update", "data": None}

       
        await tasks_collection.update_one(
            {"_id": ObjectId(id_task)},
            {"$set": body}
        )

        return {"success": True, "message": "Task updated successfully", "data": body}

    except Exception as e:
        return {"success": False, "message": str(e), "data": None}

#------------------------------------------------------------------------------------

async def delete_task(task_id: str, user_id: str) -> dict:
    try:
        task = await tasks_collection.find_one({"_id": ObjectId(task_id)})
        if not task:
            return {"success": False, "message": "Task not found", "data": None}

        list_id = task.get("id_list")
        if not list_id:
            return {"success": False, "message": "List ID not found in task", "data": None}

        list_data = await lists_collection.find_one({"_id": ObjectId(list_id)})
        if not list_data:
            return {"success": False, "message": "List not found", "data": None}

        workspace_id = list_data.get("id_workspace")
        if not workspace_id:
            return {"success": False, "message": "Workspace ID not found in list", "data": None}

        workspace = await workspaces_collection.find_one({"_id": ObjectId(workspace_id)})
        if not workspace:
            return {"success": False, "message": "Workspace not found", "data": None}

        if str(workspace.get("id_user")) != user_id:
            return {"success": False, "message": "Unauthorized", "data": None}

        await tasks_collection.delete_one({"_id": ObjectId(task_id)})

        return {"success": True, "message": "Task deleted successfully", "data": None}

    except Exception as e:
        return {"success": False, "message": str(e), "data": None}

#------------------------------------------------------------------------------------

async def move_task_to_list(task_id: str, new_list_id: str, user_id: str) -> dict:
    try:
        task = await tasks_collection.find_one({"_id": ObjectId(task_id)})
        if not task:
            return {"success": False, "message": "Task not found", "data": None}

        current_list_id = task.get("id_list")
        if not current_list_id:
            return {"success": False, "message": "Task has no associated list", "data": None}

        current_list = await lists_collection.find_one({"_id": ObjectId(current_list_id)})
        new_list = await lists_collection.find_one({"_id": ObjectId(new_list_id)})

        if not current_list or not new_list:
            return {"success": False, "message": "One or both lists not found", "data": None}

        current_workspace_id = current_list.get("id_workspace")
        new_workspace_id = new_list.get("id_workspace")

        if current_workspace_id != new_workspace_id:
            return {"success": False, "message": "Lists are not in the same workspace", "data": None}

        workspace = await workspaces_collection.find_one({"_id": ObjectId(current_workspace_id)})
        if not workspace:
            return {"success": False, "message": "Workspace not found", "data": None}

        await tasks_collection.update_one(
            {"_id": ObjectId(task_id)},
            {"$set": {"id_list": new_list_id}}
        )

        return {
            "success": True,
            "message": "Task moved successfully",
            "data": {"task_id": task_id, "new_list_id": new_list_id}
        }
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}  