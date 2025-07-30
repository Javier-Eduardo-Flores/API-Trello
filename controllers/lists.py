from models.lists import List
from utils.mongodb import get_collection
from bson import ObjectId
from pipelines.list_pipline import get_lists_with_tasks_pipeline ,count_tasks_in_list_pipeline


lists_collection = get_collection("lists")
workspaces_collection = get_collection("workspaces")
tasks_collection = get_collection("tasks")


async def create_list(list_data: List, workspace_id: str, user_id: str) -> dict:
    try:
        workspace = await workspaces_collection.find_one({"_id": ObjectId(workspace_id)})
        if not workspace:
            return {"success": False, "message": "Workspace not found", "data": None}

        if str(workspace.get("id_user")) != user_id:
            return {"success": False, "message": "Unauthorized", "data": None}

        list_dic = list_data.model_dump(exclude={"id"})
        list_dic["id_workspace"] = workspace_id

        result = await lists_collection.insert_one(list_dic)
        list_dic["id"] = str(result.inserted_id)

        return {"success": True, "message": "List created successfully", "data": list_dic}

    except Exception as e:
        return {"success": False, "message": str(e), "data": None}


#------------------------------------------------------------------------------------

async def get_lists(workspace_id: str, user_id: str) -> list:
    try:
       
        workspace = await workspaces_collection.find_one({"_id": ObjectId(workspace_id)})
        if not workspace:
            return {"success": False, "message": "Workspace not found", "data": None}

        pipeline = get_lists_with_tasks_pipeline(workspace_id)
        lists_with_tasks = await lists_collection.aggregate(pipeline).to_list(length=None)

        return {"success": True, "message": "Lists retrieved successfully", "data": lists_with_tasks}

    except Exception as e:
        return {"success": False, "message": str(e), "data": None}


#------------------------------------------------------------------------------------

async def update_list(list_id:str, user_id: str, body: dict) -> dict:
    try:
        list_data = await lists_collection.find_one({"_id": ObjectId(list_id)})
        if not list_data:
            return {"success": False, "message": "List not found", "data": None}

        workspace_id = list_data.get("id_workspace")
        workspace = await workspaces_collection.find_one({"_id": ObjectId(workspace_id)})
        if not workspace:
            return {"success": False, "message": "Workspace not found", "data": None}

        is_owner = str(workspace.get("id_user")) == user_id
        if not is_owner:
            return {"success": False, "message": "Unauthorized", "data": None}

        update_fields = {}
        if "title" in body and body["title"]:
            update_fields["title"] = body["title"]
            new_title = body["title"]
            existing_list = await lists_collection.find_one({
                "title": new_title,
                "id_workspace": workspace_id,
                "_id": {"$ne": ObjectId(list_id)}  
            })
            if existing_list:
                return {
                    "success": False,
                    "message": "Another list with this title already exists in the workspace.",
                    "data": None
                }
            update_fields["title"] = new_title

        if "description" in body:
            update_fields["description"] = body["description"]

        if not update_fields:
            return {"success": False, "message": "No fields to update", "data": None}
            
        await lists_collection.update_one(
            {"_id": ObjectId(list_id)},
            {"$set": update_fields}
        )

        updated_list = await lists_collection.find_one({"_id": ObjectId(list_id)})

        return {
            "success": True,
            "message": "List updated successfully",
            "data": {
                "id": str(updated_list["_id"]),
                "title": updated_list["title"],
                "description": updated_list.get("description"),
                "id_workspace": updated_list["id_workspace"]
            }
        }

    except Exception as e:
        return {"success": False, "message": str(e), "data": None}


#------------------------------------------------------------------------------------

async def delete_list(list_id: str, user_id: str) -> dict:
    try:
        list_data = await lists_collection.find_one({"_id": ObjectId(list_id)})
        if not list_data:
            return {"success": False, "message": "List not found", "data": None}

        workspace_id = list_data.get("id_workspace")
        workspace = await workspaces_collection.find_one({"_id": ObjectId(workspace_id)})
        if not workspace:
            return {"success": False, "message": "Workspace not found", "data": None}

        is_owner = str(workspace.get("id_user")) == user_id
        if not is_owner:
            return {"success": False, "message": "Unauthorized", "data": None}

        pipeline = count_tasks_in_list_pipeline(list_id)
        result = await tasks_collection.aggregate(pipeline).to_list(length=1)

        if result:
            task_count = result[0]["task_count"]
        else:
            task_count = 0

        if task_count > 0:
            return {
                "success": False,
                "message": "List has associated tasks and cannot be deleted",
                "data": None
            }
        await lists_collection.delete_one({"_id": ObjectId(list_id)})
        return {"success": True, "message": "List deleted successfully", "data": None}

    except Exception as e:
        return {"success": False, "message": str(e), "data": None}