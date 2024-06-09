from pydantic import BaseModel

class TestRequestDto(BaseModel):
    code: str
    language: str
    standard_ios: list
