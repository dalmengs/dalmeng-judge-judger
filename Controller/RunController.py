from Util.Singleton import Singleton
from Service.RunService import RunService
from Dto.Response.BaseResponseDto import BaseResponseDto
from Model.TestResult import TestResult
from Dto.Request.RunRequestDto import RunRequestDto

@Singleton
class RunController:
    
    __run_service: RunService = RunService()

    # 사용자의 코드를 실행합니다.
    async def run(self, run_request_dto: RunRequestDto):
        return await self.__run_service.run(
            code=run_request_dto.code,
            language=run_request_dto.language,
            standard_input=run_request_dto.standard_input
        )