from  pydantic import BaseModel, Field, field_validator
from typing import Optional
import re

class taskAssignment(BaseModel):
    id: Optional[int] = Field(default=None, description="Task Assignment ID")

    id_task: int = Field(
        description="ID of the task being assigned",
        examples=[1, 2, 3]
    )

    id_user: int = Field(
        description="ID of the user to whom the task is assigned",
        examples=[1, 2, 3]
    )

    status: str = Field(
        default="pending",
        description="Status of the task assignment",
        pattern=r"^(pending|in_progress|completed)$",
        examples=["pending", "in_progress", "completed"]
    )

    @field_validator('status')
    def validate_status(cls, value):
        if value not in ["pending", "in_progress", "completed"]:
            raise ValueError("Status must be one of 'pending', 'in_progress', or 'completed'.")
        return value