from bson import ObjectId

def get_lists_by_workspace_pipeline(workspace_id: str) -> list:
    """
    Pipeline para obtener todas las listas de un workspace específico
    """
    return [
        {
            "$match": {
                "id_workspace": workspace_id
            }
        },
        {
            "$addFields": {
                "id": {"$toString": "$_id"}
            }
        },
        {
            "$project": {
                "_id": 0,
                "id": 1,
                "title": 1,
                "description": 1,
                "id_workspace": 1
            }
        },
        {
            "$sort": {
                "title": 1
            }
        }
    ]

def get_list_by_name_in_workspace_pipeline(workspace_id: str, title: str) -> list:
    return [
         {
            "$match": {
                "id_workspace": workspace_id,
                "title": {
                    "$regex": f"^{title}$",
                    "$options": "i"  
                }
            }
        },
        {
            "$project": {
                "_id": { "$toString": "$_id" },
                "title": { "$toLower": "$title" },
                "description": { "$toLower": "$description" },
                "workspace_id": { "$toString": "$workspace_id" }
            }
        }
    ]

def count_tasks_in_list_pipeline(list_id: str) -> list:
    return [
        {
            "$match": {
                "id_list": list_id
            }
        },
        {
            "$group": {
                "_id": "$id_list",
                "task_count": {"$sum": 1}
            }
        },
        {
            "$project": {
                "_id": 0,
                "task_count": 1
            }
        }
    ]