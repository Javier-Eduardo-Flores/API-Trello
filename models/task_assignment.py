from  pydantic import BaseModel, Field, field_validator
from typing import Optional
import re

class taskAssignment(BaseModel):
    id: Optional[int] = Field(default=None, description="Task Assignment ID")

    id_task: str = Field(
        description="ID of the task being assigned",
        examples=[1, 2, 3]
    )

    id_list: str = Field(
        description="ID of the list",
        examples=[1, 2, 3]
    )

    id_member: str = Field(
        description="ID of the user to whom the task is assigned",
        examples=[1, 2, 3]
    )

    assignment_date : datetime = Field(default=None)
