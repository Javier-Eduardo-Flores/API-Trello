from  pydantic import BaseModel, Field, field_validator
from typing import Optional
import re

class Login(BaseModel):
    email: str = Field(
        pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        examples=["user@example.com", "admin@domain.co"]
    )

    password: str = Field(
        min_length=8,
        max_length=64,
        description="User password, must include at least one number, one uppercase letter, and one special character.",
    )

    @field_validator('password')
    def validate_password(cls, value):
        if not re.search(r"[a-z]", value):
            raise ValueError("The password must have at least one lowercase letter (a-z).")
       
        if not re.search(r"[A-Z]", value):
            raise ValueError("The password must have at least one uppercase letter (A-Z).")
        
        if not re.search(r"\d", value):
            raise ValueError("The password must have at least one digit (0-9).")
       
        if not re.search(r"[@$!%*?&\-/#^_]", value):
            raise ValueError("The password must have at least one special character (@$!%*?&-/#^_).")

        if not 8 <= len(value) <= 64:
            raise ValueError("The password must be between 8 and 64 characters long.")
        return value