from  pydantic import BaseModel, Field, field_validator
from typing import Optional
import re

class stateWorkspace(BaseModel):
    id: Optional[int] = Field(default=None, description="State Workspace ID")

    id_workspace: str = Field(
        description="ID of the workspace associated with the state",
        examples=["64b7f2e4a1c2b3d4e5f67890", "5f2d7c8e9a0b1c2d3e4f5678"]
    )

    id_state: str = Field(
        description="ID of the state associated with the workspace",
        examples=["64b7f2e4a1c2b3d4e5f67890", "5f2d7c8e9a0b1c2d3e4f5678"]
    )
