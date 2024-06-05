#& Imports
import os

from Util.Singleton import Singleton
from Manager.TestcaseManager import TestcaseManager

@Singleton
class TestcaseService:
    
    __testcase_manager: TestcaseManager = TestcaseManager()

    # 특정 문제의 테스트케이스의 정보를 반환합니다.
    async def get_testcase_info(self, problem_id: int):
        return await self.__testcase_manager.get_testcase_info(
            problem_id=problem_id
        )
    
    # 특정 문제의 테스트케이스의 개수를 반환합니다.
    async def get_testcase_count(self, problem_id: int):
        return await self.__testcase_manager.get_testcase_count(
            problem_id=problem_id
        )
    
    # 특정 문제의 테스트케이스를 반환합니다.
    async def get_testcase(self, problem_id: int, testcase_id: int):
        return await self.__testcase_manager.get_testcase(
            problem_id=problem_id,
            testcase_id=testcase_id
        )