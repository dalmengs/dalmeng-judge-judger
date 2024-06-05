from pydantic import BaseModel
from typing import Optional

class TestcaseInfoRequestDto(BaseModel):
    problem_id: int
    testcase_id: Optional[int] = 0
