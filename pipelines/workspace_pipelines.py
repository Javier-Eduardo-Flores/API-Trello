from bson import ObjectId

def get_lists_in_workspace_pipeline(workspace_id: str) -> list:
    return [
        {
            "$match": {
                "_id": ObjectId(workspace_id)
            }
        },
        {
            "$lookup": {
                "from": "lists",
                "localField": "_id",
                "foreignField": "id_workspace",
                "as": "lists"
            }
        },
        {
            "$project": {
                "list_count": {"$size": "$lists"}
            }
        }
    ]
