from pydantic import BaseModel

class TestcaseInfoRequestDto(BaseModel):
    problem_id: int
