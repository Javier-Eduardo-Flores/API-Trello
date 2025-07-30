from models.workspaces import Workspace
from utils.mongodb import get_collection
from bson import ObjectId
from fastapi import HTTPException
from pipelines.workspace_pipelines import get_lists_in_workspace_pipeline

workspaces_collection = get_collection("workspaces")
users_collection = get_collection("users")


#------------------------------------------------------------------------------------
async def create_workspace(workspace: Workspace, user_id: str) -> dict:
    """
    Create a new workspace and associate it with the user.
    """
    try:
        
        user = await users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            return {"success": False, "message": "User not found", "data": None}

        workspace_dict = workspace.model_dump(exclude={"id"})
        workspace_dict["id_user"] = ObjectId(user_id)

        result = await workspaces_collection.insert_one(workspace_dict)
        inserted_id = result.inserted_id

        response_data = workspace.model_dump()
        response_data["id"] = str(inserted_id)
        response_data["id_user"] = user_id

        return {"success": True, "message": "Workspace created successfully", "data": response_data}

    except Exception as e:
        return {"success": False, "message": str(e), "data": None}

#------------------------------------------------------------------------------------

async def get_workspaces(skip: int = 0, limit: int = 50, user_id: str = None) -> dict:
    
    try:
        if user_id:
            user_exists = await users_collection.find_one({"_id": ObjectId(user_id)})
            if not user_exists:
                return {"success": False, "message": "User not found", "data": None}
        
            pipeline = [
                {"$match": {"id_user": user_id}},
                {"$skip": skip},
                {"$limit": limit}
            ]

        else:
              pipeline = [
                {"$skip": skip},
                {"$limit": limit}
            ]
        workspaces = await workspaces_collection.aggregate(pipeline).to_list(length=None)  

        return {
            "success": True,
            "message": "Workspaces retrieved successfully",
            "data": workspaces
        }
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}

#------------------------------------------------------------------------------------

async def update_workspace(workspace_id: str, user_id: str, body: dict) -> dict:
    try:
        workspace = await workspaces_collection.find_one({"_id": ObjectId(workspace_id)})
        if not workspace:
            return {"success": False, "message": "Workspace not found", "data": None}

        if str(workspace.get("id_user")) != user_id:
            return {"success": False, "message": "Unauthorized", "data": None}

        new_name = body.get("name")
        if new_name and new_name != workspace.get("name"):
            existing = await workspaces_collection.find_one({
                "name": new_name,
                "id_user": ObjectId(user_id),
                "_id": {"$ne": ObjectId(workspace_id)}
            })
            if existing:
                return {
                    "success": False,
                    "message": "You already have a workspace with that name.",
                    "data": None
                }

        await workspaces_collection.update_one(
            {"_id": ObjectId(workspace_id)},
            {"$set": body}
        )

        return {
            "success": True,
            "message": "Workspace updated successfully",
            "data": body
        }

    except Exception as e:
        return {"success": False, "message": str(e), "data": None}


#------------------------------------------------------------------------------------


async def delete_workspace(workspace_id: str, user_id: str) -> dict:
     try:

        workspace = await workspaces_collection.find_one({"_id": ObjectId(workspace_id)})

        if not workspace:
            return {"success": False, "message": "Workspace not found", "data": None}

        if str(workspace["id_user"]) != user_id:
            return {"success": False, "message": "You are not authorized to delete this workspace", "data": None}

        pipeline = get_lists_in_workspace_pipeline(workspace_id)
        result = await workspaces_collection.aggregate(pipeline).to_list(length=1)

        if not result:
            return {"success": False, "message": "Workspace not found", "data": None}

        list_count = result[0]["list_count"]
        if list_count > 0:
            return {"success": False, "message": "Workspace has associated lists and cannot be deleted", "data": None}

        
        await workspaces_collection.delete_one({"_id": ObjectId(workspace_id)})
        return {"success": True, "message": "Workspace deleted successfully", "data": None}

     except Exception as e:
        return {"success": False, "message": str(e), "data": None}