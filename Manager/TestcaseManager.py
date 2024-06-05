#& Imports
import os

from Util.Singleton import Singleton
from Exception.Exceptions import *

@Singleton
class TestcaseManager:
    __testcase_base_dir = "./Testcases"

    # 특정 문제의 테스트케이스 정보를 반환합니다.
    # - 테스트케이스의 개수
    # - 각 테스트케이스에 대하여 입력과 출력 데이터의 크기(Byte)
    # - 각 테스트케이스에 대하여 입력과 출력 데이터의 토큰 개수와 줄개수 
    async def get_testcase_info(self, problem_id: int):
        ret = {
            "number_of_testcases": 0,
            "testcase_info": []
        }

        # 해당 아이디의 문제가 존재하는지 판단합니다.
        if not await self.__check_problem_exists(problem_id): raise ProblemNotFoundException

        # 테스트케이스의 개수를 셉니다.
        testcase_count = len(os.listdir(f"{self.__testcase_base_dir}/{problem_id}")) // 2
        ret["number_of_testcases"] = testcase_count
        
        # 각 테스트케이스의 정보를 만듭니다.
        for testcase_number in range(1, testcase_count + 1):
            # 입출력 데이터의 크기를 측정합니다.
            input_size = os.path.getsize(f"{self.__testcase_base_dir}/{problem_id}/{testcase_number}.in")
            output_size = os.path.getsize(f"{self.__testcase_base_dir}/{problem_id}/{testcase_number}.out")
            
            # 입력 데이터의 토큰 수와 줄수를 구합니다.
            input_file = open(f"{self.__testcase_base_dir}/{problem_id}/{testcase_number}.in", "r")
            input_data = input_file.read().strip("\n").split("\n")
            input_tokens = 0
            for line in input_data:
                input_tokens += len(line.strip(" ").split(" "))
            input_file.close()

            # 출력 데이터의 토큰 수와 줄수를 구합니다.
            output_file = open(f"{self.__testcase_base_dir}/{problem_id}/{testcase_number}.out", "r")
            output_data = output_file.read().strip("\n").split("\n")
            output_tokens = 0
            for line in output_data:
                output_tokens += len(line.strip(" ").split(" "))
            output_file.close()

            ret["testcase_info"].append({
                "testcase_id": testcase_number,
                "input_size": input_size,
                "output_size": output_size,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "input_line": len(input_data),
                "output_lines": len(output_data)
            })
        return ret
    
    # 특정 문제의 테스트케이스 개수를 반환합니다.
    async def get_testcase_count(self, problem_id: int):
        # 해당 아이디의 문제가 존재하는지 판단합니다.
        if not await self.__check_problem_exists(problem_id): raise ProblemNotFoundException

        # 테스트케이스의 개수를 셉니다.
        testcase_count = len(os.listdir(f"{self.__testcase_base_dir}/{problem_id}")) // 2
        return testcase_count
    
    # 테스트케이스를 반환합니다.
    # - testcase_id가 0이면 모든 테스트케이스를 반환합니다.
    async def get_testcase(self, problem_id: int, testcase_id: int = 0):

        # 해당 아이디의 문제와 테스트케이스가 존재하는지 판단합니다.
        if not await self.__check_problem_exists(problem_id): raise ProblemNotFoundException
        if testcase_id and not await self.__check_testcase_exists(problem_id, testcase_id): raise TestcaseNotFoundException

        l, r = testcase_id, testcase_id + 1
        if testcase_id == 0:
            l, r = 1, len(os.listdir(f"{self.__testcase_base_dir}/{problem_id}")) // 2 + 1

        ret = []
        for testcase_number in range(l, r):
            # 입출력 파일을 읽습니다.
            input_file = open(f"{self.__testcase_base_dir}/{problem_id}/{testcase_number}.in", "r")
            output_file = open(f"{self.__testcase_base_dir}/{problem_id}/{testcase_number}.out", "r")

            # 입출력 데이터를 추가합니다.
            ret.append({
                "testcase_id": testcase_number,
                "input_data": input_file.read().strip("\n"),
                "output_data": output_file.read().strip("\n")
            })

            # 입출력 파일을 닫습니다.
            input_file.close()
            output_file.close()
        
        if testcase_id == 0: return ret
        return ret[0]
    
    async def __check_problem_exists(self, problem_id: int) -> bool:
        return os.path.exists(f"{self.__testcase_base_dir}/{problem_id}")
    
    async def __check_testcase_exists(self, problem_id: int, testcase_id: int) -> bool:
        if not await self.__check_problem_exists(problem_id):
            return False
        return os.path.exists(f"{self.__testcase_base_dir}/{problem_id}/{testcase_id}.out")