from bson import ObjectId

def get_lists_in_workspace_pipeline(workspace_id: str) -> list:
    return [
        {
            "$match": {
                "_id": ObjectId(workspace_id)
            }
        },
        {
            "$addFields": {
                "id_str": {"$toString": "$_id"} 
            }
        },
        {
            "$lookup": {
                "from": "lists",
                "localField": "id_str",       
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