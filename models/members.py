from  pydantic import BaseModel, Field, field_validator
from typing import Optional
import re

class member(BaseModel):
   id_user:str = Field(default=None, description="Member ID")

   id_workspace: str = Field(
       description="ID of the workspace associated with the member",
       examples=["64b7f2e4a1c2b3d4e5f67890", "5f2d7c8e9a0b1c2d3e4f5678"]
   )

   
