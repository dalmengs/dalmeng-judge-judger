from pydantic import BaseModel
from typing import Optional

class TestcaseInfoRequestDto(BaseModel):
    problem_id: int
