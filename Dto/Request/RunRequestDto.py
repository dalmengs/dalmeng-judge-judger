from pydantic import BaseModel
from typing import Optional

class RunRequestDto(BaseModel):
    code: str
    language: str
    standard_input: str
