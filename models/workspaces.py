from  pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from models.members import member
import re

class Workspace(BaseModel):
    id: Optional[str] = Field(default=None, description="Workspace ID")

    name: str = Field(
        description="Workspace name",
        min_length=1,
        max_length=100,
        examples=["Marketing Team", "Development Team"]
    )

    description: Optional[str] = Field(
        default=None,
        description="Detailed description of the workspace",
        max_length=500,
        examples=["This workspace is for the marketing team to collaborate on campaigns and strategies."]
    )

    id_user: Optional[str] = Field(
        default=None,
        description="ID of the user who owns the workspace",
    )

    @field_validator('name')
    def validate_name(cls, value):
        if not re.match(r'^[a-zA-Z0-9\s]+$', value):
            raise ValueError("Name must contain only alphanumeric characters and spaces.")
        return value