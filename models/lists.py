from  pydantic import BaseModel, Field, field_validator
from typing import Optional
import re

class List(BaseModel):
    id: Optional[str] = Field(default=None, description="List ID")

    title: str = Field(
        description="List title",
        min_length=1,
        max_length=100,
        examples=["To Do", "In Progress", "Done"]
    )

    description: Optional[str] = Field(
        default=str(""),
        description="Detailed description of the list",
        max_length=500,
        examples=["Tasks that need to be completed in this list."]
    )
    id_workspace: Optional[str] = Field(
        default=None,
        description="ID of the workspace to which this list belongs",
    )

    @field_validator('title')
    def validate_title(cls, value):
        if not re.match(r'^[\w\s-]+$', value):
            raise ValueError("Title can only contain alphanumeric characters, spaces, and hyphens.")
        return value.strip()