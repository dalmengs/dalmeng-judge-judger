from pydantic import BaseModel
from typing import Optional

class BaseResponseDto(BaseModel):

    status_code: int
    msg: str
    data: Optional[object]

    @staticmethod
    def ok(status_code: int = 200, msg: str = "succeed", data: object = None):
        try:
            return {
                "status_code": status_code,
                "msg": msg,
                "data": data.to_dict()
            }
        except:
            return {
                "status_code": status_code,
                "msg": msg,
                "data": data
            }

    @staticmethod
    def failed(status_code: int = 400, msg: str = "failed", data: object = None, exception: Exception = None):
        if exception:
            return {
                "status_code": exception.code,
                "msg": exception.msg,
                "data": data
            }
        return {
            "status_code": status_code,
            "msg": msg,
            "data": data
        }
    