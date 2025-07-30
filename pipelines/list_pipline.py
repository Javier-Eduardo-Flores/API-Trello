from bson import ObjectId

def get_lists_with_tasks_pipeline(workspace_id: str) -> list:
    return [
        {
            "$match": {
                "id_workspace": ObjectId(workspace_id)
            }
        },
        {
            "$lookup": {
                "from": "tasks",
                "localField": "_id",
                "foreignField": "id_list",
                "as": "tasks"
            }
        },
        {
            "$project": {
                "_id": {"$toString": "$_id"},
                "title": 1,
                "description": 1,
                "id_workspace": 1,
                "tasks": {
                    "$map": {
                        "input": "$tasks",
                        "as": "task",
                        "in": {
                            "id": {"$toString": "$$task._id"},
                            "title": "$$task.title",
                            "description": "$$task.description",
                            "id_list": "$$task.id_list",
                        }
                    }
                }
            }
        }
    ]

def count_tasks_in_list_pipeline(list_id: str) -> list:
    return [
        {
            "$match": {
                "id_list": ObjectId(list_id)
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