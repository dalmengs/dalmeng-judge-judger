from pydantic import BaseModel
from typing import Optional

class JudgeRequestDto(BaseModel):
    problem_id: int
    code: str
    language: str
    time_limit: float
    memory_limit: int
