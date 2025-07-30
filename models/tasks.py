from  pydantic import BaseModel, Field, field_validator
from typing import Optional
import re

class Task(BaseModel):
    id: Optional[str] = Field(default=None, description="Task ID")

    title: str = Field(
        description="Task title",
        min_length=1,
        max_length=100,
        examples=["Complete project report", "Prepare presentation for meeting"]
    )

    id_list: str = Field(
        default=None,
        description="ID of the list to which the task belongs"
    )
    
    description: Optional[str] = Field(
        default=None,
        description="Detailed description of the task",
        max_length=500,
        examples=["Write a detailed report on the project progress and outcomes."]
    )

    
    @field_validator('title')
    def validate_title(cls, value):
        if not re.match(r'^[a-zA-Z0-9\s]+$', value):
            raise ValueError("Title must contain only alphanumeric characters and spaces.")
        return value

    
    