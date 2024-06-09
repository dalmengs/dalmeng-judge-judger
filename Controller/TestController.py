import json
from Util.Singleton import Singleton
from Service.TestService import TestService
from Dto.Response.BaseResponseDto import BaseResponseDto
from Model.TestResult import TestResult
from Dto.Request.JudgeRequestDto import JudgeRequestDto

from Dto.Request.TestRequestDto import TestRequestDto

@Singleton
class TestController:
    
    __test_service: TestService = TestService()

    # 사용자의 코드를 테스트합니다.
    async def test(self, test_request_dto: TestRequestDto):
        async for test_result in self.__test_service.test(
            code=test_request_dto.code,
            language=test_request_dto.language,
            standard_ios=test_request_dto.standard_ios
        ):
            if isinstance(test_result, TestResult):
                yield (json.dumps(
                    BaseResponseDto.ok(
                        data=test_result.to_dict()
                    ), ensure_ascii=False
                ) + "\n")
            else:
                yield (json.dumps(
                    BaseResponseDto.ok(
                        status_code=100,
                        data=test_result.to_dict()
                    ), ensure_ascii=False
                ) + "\n")

    