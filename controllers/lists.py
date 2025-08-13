from models.lists import List
from utils.mongodb import get_collection
from bson import ObjectId
from fastapi import HTTPException
from pipelines.list_pipline import get_lists_by_workspace_pipeline ,count_tasks_in_list_pipeline, get_list_by_name_in_workspace_pipeline

lists_collection = get_collection("lists")
workspaces_collection = get_collection("workspaces")
tasks_collection = get_collection("tasks")

async def create_list(list_data: List, workspace_id: str, user_id: str) -> dict:

    try:
        workspace =  workspaces_collection.find_one({"_id": ObjectId(workspace_id)})
        if not workspace:
            return {"success": False, "message": "Workspace not found", "data": None}

        if workspace["id_user"] != user_id:
            return {"success": False, "message": "Unauthorized", "data": None}

        title = list_data.title.strip().lower()
        description = list_data.description.strip().lower()

        existing_list = lists_collection.aggregate(
            get_list_by_name_in_workspace_pipeline(workspace_id, title)
        )
        existing_list = list(existing_list)

        if existing_list:
            raise HTTPException(status_code=400, detail="List with this title already exists in the workspace.")

        list_dic = list_data.model_dump(exclude={"id"})
        list_dic["id_workspace"] = workspace_id

        result =  lists_collection.insert_one(list_dic)
        inserted_id = result.inserted_id

        response_data = {
            "id": str(inserted_id),
            "title": list_data.title,
            "description": list_data.description,
            "id_workspace": workspace_id
        }
        return {"success": True, "message": "List created successfully", "data": response_data}

    except Exception as e:
        return {"success": False, "message": str(e), "data": None}


#------------------------------------------------------------------------------------

async def get_lists(workspace_id: str) -> list:
    try:
       
        workspace =  workspaces_collection.find_one({"_id": ObjectId(workspace_id)})
        if not workspace:
            return {"success": False, "message": "Workspace not found", "data": None}

        pipeline = get_lists_by_workspace_pipeline(workspace_id)
        lists_with_tasks =  lists_collection.aggregate(pipeline)
        lists_with_tasks = list(lists_with_tasks)

        return {"success": True, "message": "Lists retrieved successfully", "data": lists_with_tasks}

    except Exception as e:
        return {"success": False, "message": str(e), "data": None}

#------------------------------------------------------------------------------------

async def get_list_by_id (list_id:str, workspace_id:str)-> dict:
   try:
        workspace = workspaces_collection.find_one({"_id": ObjectId(workspace_id)})
        if not workspace:
            return {"success": False, "message": "Workspace not found", "data": None}
        list_data = lists_collection.find_one({"_id": ObjectId(list_id), "id_workspace": workspace_id})
        if not list_data:
            return {"success": False, "message": "List not found", "data": None}

        response_data = {
            "id": str(list_data["_id"]),
            "title": list["title"],
            "description": list["description"],
            "id_workspace": list["id_workspace"]
        }
        return {"success": True, "message": "List retrieved successfully", "data": response_data}

   except Exception as e:
        return {"success": False, "message": str(e), "data": None}

#------------------------------------------------------------------------------------
 
async def update_list(list_id: str, user_id: str, list_data: List) -> dict:
    try:
       
        existing_list =  lists_collection.find_one({"_id": ObjectId(list_id)})
        if not existing_list:
            return {"success": False, "message": "List not found", "data": None}

        workspace_id = existing_list["id_workspace"]
        workspace =  workspaces_collection.find_one({"_id": ObjectId(workspace_id)})
        if not workspace:
            return {"success": False, "message": "Workspace not found", "data": None}

        if workspace["id_user"] != user_id:
            return {"success": False, "message": "Unauthorized", "data": None}


        if not list_data.title:
            list_data.title = existing_list["title"]
        if not list_data.description:
            list_data.description = existing_list["description"]

        list_data.title = list_data.title.strip()
        list_data.description = list_data.description.strip()
        list_data.id_workspace = workspace_id

        if list_data.title == existing_list["title"] and list_data.description == existing_list["description"]:
            return {"success": False, "message": "You are not making changes to the list", "data": None}

        list_duplicate = lists_collection.aggregate(
            get_list_by_name_in_workspace_pipeline(workspace_id, list_data.title)
        )

        if list_data.description == existing_list["description"]:

            if list(list_duplicate):
                raise HTTPException(status_code=400, detail="List with this title already exists in the workspace.")

        
        result = lists_collection.update_one(
            {"_id": ObjectId(list_id)},
            {"$set": list_data.model_dump(exclude={"id"})}
        )

        if result.modified_count == 0:
            return {"success": False, "message": "List not found or no changes made", "data": None}

        
        response_data = {
            "id": list_id,
            "title": list_data.title,
            "description": list_data.description,
            "id_workspace": workspace_id
        }

        return {
            "success": True,
            "message": "List updated successfully",
            "data": response_data
        }

    except Exception as e:
        return {"success": False, "message": str(e), "data": None}

#------------------------------------------------------------------------------------

async def delete_list(list_id: str, user_id: str) -> dict:
    try:
        list_data =  lists_collection.find_one({"_id": ObjectId(list_id)})
        if not list_data:
            return {"success": False, "message": "List not found", "data": None}

        workspace_id = list_data.get("id_workspace")
        workspace =  workspaces_collection.find_one({"_id": ObjectId(workspace_id)})
        if not workspace:
            return {"success": False, "message": "Workspace not found", "data": None}

        is_owner = str(workspace.get("id_user")) == user_id
        if not is_owner:
            return {"success": False, "message": "Unauthorized", "data": None}

        pipeline = count_tasks_in_list_pipeline(list_id)
        result =  tasks_collection.aggregate(pipeline)
        result = list(result)
# Si hay algun error borrar el .to_list

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

        lists_collection.delete_one({"_id": ObjectId(list_id)})
        return {"success": True, "message": "List deleted successfully", "data": None}

    except Exception as e:
        return {"success": False, "message": str(e), "data": None}