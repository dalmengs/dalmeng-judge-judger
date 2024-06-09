from pydantic import BaseModel

class JudgeRequestDto(BaseModel):
    problem_id: int
    code: str
    language: str
    time_limit: float
    memory_limit: int
