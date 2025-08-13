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
        
        user =  users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            return {"success": False, "message": "User not found", "data": None}

        workspace.name = workspace.name.strip()
        workspace.description = workspace.description.strip()

        existing_workspace =  workspaces_collection.find_one({
            "name": {"$regex": f"^{workspace.name}$", "$options": "i"},
            "id_user": user_id
        })

        if existing_workspace:
            raise HTTPException(status_code=400, detail="You already have a workspace with that name.")
        
        workspace_dict = workspace.model_dump(exclude={"id", "id_user"})
        workspace_dict["id_user"] = user_id

        result =  workspaces_collection.insert_one(workspace_dict)
        inserted_id = result.inserted_id

        response_data = {
            "id": str(inserted_id),
            "name": workspace.name,
            "description": workspace.description,
            "id_user": user_id
        }

        return {"success": True, "message": "Workspace created successfully", "data": response_data}

    except Exception as e:
        return {"success": False, "message": str(e), "data": None}

#------------------------------------------------------------------------------------

async def get_workspaces(skip: int = 0, limit: int = 50, user_id: str = None) -> dict:
    
    try:
        if user_id:
            user_exists =  users_collection.find_one({"_id": ObjectId(user_id)})
            if not user_exists:
                return {"success": False, "message": "User not found", "data": None}
        
            pipeline = [
                {"$match": {"id_user": user_id}},
                {"$skip": skip},
                {"$limit": limit},
                {
                    "$addFields": {
                        "id": {"$toString": "$_id"}
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "id": 1,
                        "name": 1,
                        "description": 1,
                        "id_user": 1
                    }
                }
            ]

        else:
              pipeline = [
                {"$skip": skip},
                {"$limit": limit},
                {
                    "$addFields": {
                        "id": {"$toString": "$_id"}
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "id": 1,
                        "name": 1,
                        "description": 1,
                        "id_user": 1
                    }
                }
            ]
        cursor = workspaces_collection.aggregate(pipeline)
        workspaces =  cursor.to_list(length=None)  

        if not workspaces:
            return {"success": False, "message": "No workspaces found", "data": None}

        return {
            "success": True,
            "message": "Workspaces retrieved successfully",
            "data": workspaces
        }
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}

#------------------------------------------------------------------------------------

async def get_workspace_by_id(workspace_id: str, user_id: str ) -> dict:
    try: 
        workspace =  workspaces_collection.find_one({"_id": ObjectId(workspace_id)})
        if not workspace:
            return {"success": False, "message": "Workspace not found", "data": None}

        response_data = {
            "id": str(workspace["_id"]),
            "name": workspace["name"],
            "description": workspace.get("description"),
            "id_user": workspace["id_user"]
        }

        return {"success": True, "message": "Workspace retrieved successfully", "data": response_data}
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}


#------------------------------------------------------------------------------------

async def update_workspace(workspace_id: str, user_id: str, workspace: Workspace) -> dict:
    try:
        workspace = Workspace(**workspace) 
        workspace_data =  workspaces_collection.find_one({"_id": ObjectId(workspace_id)})
        if not workspace_data:
            return {"success": False, "message": "Workspace not found", "data": None}

        if workspace_data["id_user"] != user_id:
            return {"success": False, "message": "Unauthorized", "data": None}

        if  not workspace.name:
            workspace.name = workspace_data["name"]
        if not workspace.description:
            workspace.description = workspace_data["description"]
        workspace.id_user = user_id
        workspace.name = workspace.name.strip()
        workspace.description = workspace.description.strip()

        if workspace.name == workspace_data["name"] and workspace.description == workspace_data["description"]:
            return {"success": False, "message": "You are not making changes to the workspace", "data": None}

        existing_workspace =  workspaces_collection.find_one({
                "name": {"$regex": f"^{workspace.name}$", "$options": "i"},
                "id_user": user_id,
                "_id": {"$ne": ObjectId(workspace_id)}
                 })


        if workspace.description == workspace_data["description"]:
            if existing_workspace:
                raise HTTPException(status_code=400, detail="You already have a workspace with that name.")
            

        result =  workspaces_collection.update_one(
            {"_id": ObjectId(workspace_id)},
            {"$set": workspace.model_dump(exclude={"id"})}
        )
     
        if result.modified_count == 0:
            return {"success": False, "message": "Workspace not found", "data": None}  

        response_data = {
            "id":workspace_id,
            "name":workspace.name,
            "description":workspace.description,
            "user_id":user_id
        }
        return {
            "success": True,
            "message": "Workspace updated successfully",
            "data": response_data
        }

    except Exception as e:
        return {"success": False, "message": str(e), "data": None}

#------------------------------------------------------------------------------------
# pendiente por revisar si se puede eliminar el workspace si tiene listas asociadas

async def delete_workspace(workspace_id: str, user_id: str) -> dict:
     try:

        workspace =  workspaces_collection.find_one({"_id": ObjectId(workspace_id)})

        if not workspace:
            return {"success": False, "message": "Workspace not found", "data": None}

        if workspace["id_user"] != user_id:
            return {"success": False, "message": "You are not authorized to delete this workspace", "data": None}

        pipeline = get_lists_in_workspace_pipeline(workspace_id)
        cursor = workspaces_collection.aggregate(pipeline)
        result =  list(cursor)

        if not result:
            return {"success": False, "message": "Workspace not found", "data": None}

        list_count = result[0]["list_count"]
        if list_count > 0:
            return {"success": False, "message": "Workspace has associated lists and cannot be deleted", "data": None}

        workspaces_collection.delete_one({"_id": ObjectId(workspace_id)})
        return {"success": True, "message": "Workspace deleted successfully", "data": None}

     except Exception as e:
        return {"success": False, "message": str(e), "data": None}