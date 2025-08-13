from bson import ObjectId

def get_task_by_title_in_workspace_pipeline(workspace_id: str, title: str) -> list:
      return [
        {
            "$match": {
                "title": {
                    "$regex": f"^{title}$",
                    "$options": "i"
                }
            }
        },
        {
            "$addFields": {
                "id_list_obj": { "$toObjectId": "$id_list" }
            }
        },
        {
            "$lookup": {
                "from": "lists",
                "localField": "id_list_obj",
                "foreignField": "_id",
                "as": "list_data"
            }
        },
        {
            "$unwind": "$list_data"
        },
        {
            "$match": {
                "list_data.id_workspace": workspace_id   
            }
        },
        {
            "$project": {
                "_id": 1
            }
        }
    ]

def get_tasks_by_workspace_pipeline(workspace_id: str) -> list:
    return [
        {
           
            "$addFields": {
                "id_list_obj": {"$toObjectId": "$id_list"}
            }
        },
        {
            "$lookup": {
                "from": "lists",
                "localField": "id_list_obj",
                "foreignField": "_id",
                "as": "list_data"
            }
        },
        {
            "$unwind": "$list_data"
        },
        {
            "$match": {
                "list_data.id_workspace": workspace_id
            }
        },
        {
            "$sort": {
                "id_list": 1
            }
        },
        {
            "$project": {
                "_id": {"$toString": "$_id"},
                "title": 1,
                "description": 1,
                "id_list": 1,
                "list_title": "$list_data.title"
            }
        }
    ]