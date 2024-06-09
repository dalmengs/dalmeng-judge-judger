from Util.Singleton import Singleton
from Service.TestcaseService import TestcaseService
from Dto.Request.TestcaseInfoRequestDto import TestcaseInfoRequestDto
from Dto.Request.TestcaseRequestDto import TestcaseInfoRequestDto

@Singleton
class TestcaseController:
    
    __testcase_service: TestcaseService = TestcaseService()

    # 특정 문제의 테스트케이스의 정보를 반환합니다.
    async def get_testcase_info(self, testcase_info_request_dto: TestcaseInfoRequestDto) -> int:
        return await self.__testcase_service.get_testcase_info(
            problem_id=testcase_info_request_dto.problem_id
        )
    
    # 특정 문제의 테스트케이스를 반환합니다.
    async def get_testcase(self, testcase_reqeust_dto: TestcaseInfoRequestDto):
        return await self.__testcase_service.get_testcase(
            problem_id=testcase_reqeust_dto.problem_id,
            testcase_id=testcase_reqeust_dto.testcase_id
        )