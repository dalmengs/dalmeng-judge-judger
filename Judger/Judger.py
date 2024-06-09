import os
import time
import psutil
import shutil
import asyncio

from Util.Util import get_random_id
from Util.EnvironmentVariable import env
from Util.Singleton import Singleton
from Service.TestcaseService import TestcaseService
from Model.JudgeResult import JudgeResult
from Model.TestResult import TestResult
from Model.PartialResult import PartialResult
from Model.RunResult import RunResult
from Exception.Exceptions import *

@Singleton
class Judger:

    __code_file_base_dir = "./Code"
    __testcase_service: TestcaseService = TestcaseService()

    # 언어 별 컴파일 커맨드입니다.
    __compile_command = {
        "cpp": "g++ ./Code/{file_id}/Solution.cpp -o ./Code/{file_id}/Solution -O2 -Wall -lm -std=gnu++17",
        "c": "gcc ./Code/{file_id}/Solution.c -o ./Code/{file_id}/Solution -O2 -Wall -lm -std=gnu11",
        "java": "javac -J-Xms1024m -J-Xmx1024m -J-Xss1024m -encoding UTF-8 ./Code/{file_id}/Solution.java",
        "py": "python3 -W ignore -c \"import py_compile; py_compile.compile(r'./Code/{file_id}/Solution.py')\""
    }
    # 언어 별 실행 커맨드입니다.
    __run_command = {
        "cpp": "./Code/{file_id}/Solution",
        "c": "./Code/{file_id}/Solution",
        "java": "cd ./Code/{file_id} && java -Xms1024m -Xmx1024m -Xss1024m -Dfile.encoding=UTF-8 Solution",
        "py": "python3 -W ignore ./Code/{file_id}/Solution.py"
    }

    # 프로그램 테스트 / 실행 시 기본으로 적용되는 시간 / 메모리 제한입니다.
    __run_time_limit = float(env("DEFAULT_TIME_LIMIT"))
    __run_memory_limit = int(env("DEFAULT_MEMORY_LIMIT"))

    # [실행 모드] 사용자의 코드를 실행합니다.
    async def run(self, code: str, language: str, standard_input: str):
        # 파일을 만듭니다.
        file_id = self.make_file(code=code, language=language)

        # 컴파일을 합니다.
        compile_result = await self.compile(language=language, file_id=file_id)

        # 컴파일 오류가 난 경우입니다.
        if compile_result["is_error"]:
            self.remove_file(file_id=file_id)
            return RunResult(
                run_result=1,
                code=code,
                language=language,
                code_length=len(code.encode('utf-8')),
                file_id=file_id,
                standard_input=standard_input,
                standard_output="컴파일 중 오류가 발생하였습니다.\n\n" + compile_result["stderr"]
            )
        
        await self.__dummy_run_program(language, file_id)

        # 프로그램을 실행합니다.
        test_result = await self.run_program(
            language=language,
            time_limit=self.__run_time_limit,
            memory_limit=self.__run_memory_limit,
            standard_input=standard_input,
            file_id=file_id
        )

        # 시간 초과 / 메모리 초과 / 런타임 오류가 발생한 경우입니다.
        if test_result["execution_result"]:
            execution_result_messages = {2: "프로그램 실행 제한 시간을 초과했습니다.", 3: "프로세스에 할당된 메모리를 전부 사용했습니다.", 5: "프로그램 실행 중 오류가 발생했습니다."}

            self.remove_file(file_id=file_id)
            return RunResult(
                run_result=test_result["execution_result"],
                code=code,
                language=language,
                code_length=len(code.encode('utf-8')),
                file_id=file_id,
                standard_input=standard_input,
                standard_output=execution_result_messages[test_result["execution_result"]] + "\n\n{}".format(test_result["message"])
            )
        
        # 정상적으로 프로세스가 종료된 경우입니다.
        return RunResult(
            run_result=test_result["execution_result"],
            code=code,
            language=language,
            code_length=len(code.encode('utf-8')),
            file_id=file_id,
            standard_input=standard_input,
            standard_output=test_result["stdout"],
            execution_time=test_result["execution_time"],
            memory_usage=test_result["memory_usage"]
        )


    # [테스트 모드] 사용자의 코드를 테스트합니다.
    async def test(self, code: str, language: str, standard_ios: list):

        # 파일을 만듭니다.
        file_id = self.make_file(code=code, language=language)

        yield PartialResult(
            status_code=1,
            message="컴파일 중..."
        )

        # 컴파일을 진행합니다.
        compile_result = await self.compile(language=language, file_id=file_id)

        # 컴파일 오류가 뜬 경우입니다.
        if compile_result["is_error"]:
            yield PartialResult(
                status_code=7,
                message="컴파일 오류"
            )
            yield TestResult(
                test_result=0,
                code=code,
                language=language,
                code_length=len(code.encode('utf-8')),
                msg=compile_result["stderr"],
                file_id=file_id
            )
            self.remove_file(file_id=file_id)
            return
        
        await self.__dummy_run_program(language, file_id)
        
        testcase_result = []
        accepted_count = 0

        # 테스트를 진행합니다.
        for testcase in standard_ios:
            standard_input = testcase["standard_input"]
            expected_output = testcase["expected_output"]

            # 프로그램을 실행합니다.
            test_result = await self.run_program(
                language=language,
                time_limit=self.__run_time_limit,
                memory_limit=self.__run_memory_limit,
                standard_input=standard_input,
                file_id=file_id
            )

            judge_result = {
                "testcase_id": len(testcase_result),
                "is_passed": False,
                "message": None,
                "standard_output": None,
                "execution_time": None,
                "memory_usage": None
            }

            # 시간 초과 / 메모리 초과 / 런타임 오류가 난 경우입니다.
            if test_result["execution_result"]:
                execution_result_messages = {2: "시간 초과", 3: "메모리 초과", 5: "런타임 오류"}

                judge_result["message"] = test_result["message"]
                yield PartialResult(
                    status_code=test_result["execution_result"] + 3,
                    message=execution_result_messages[test_result["execution_result"]],
                    data=judge_result
                )
                testcase_result.append(judge_result)
                continue
            
            # 실제 출력과 예상 출력을 비교합니다.
            jury_result = self.compare_answer(test_result["stdout"], expected_output)

            judge_result["is_passed"] = jury_result["is_accepted"]
            judge_result["message"] = jury_result["jury_result"]
            judge_result["execution_time"] = test_result["execution_time"]
            judge_result["memory_usage"] = test_result["memory_usage"]
            judge_result["standard_output"] = test_result["stdout"]

            testcase_result.append(judge_result)

            # 예상과 출력이 다른 경우입니다.
            if not jury_result["is_accepted"]:
                yield PartialResult(
                    status_code=4,
                    message="테스트 실패",
                    data=judge_result
                )
            # 예상과 출력이 같은 경우입니다.
            else:
                accepted_count += 1
                yield PartialResult(
                    status_code=3,
                    message="테스트 성공!",
                    data=judge_result
                )
        
        msg = "모든 테스트를 성공했습니다!"
        if accepted_count == 0 and len(testcase):
            msg = "모든 테스트를 실패했습니다."
        elif accepted_count and accepted_count != len(testcase):
            msg = "{testcase_count}개의 테스트 중 {accepted_count}개를 성공하였습니다.".format(
                testcase_count = len(standard_ios),
                accepted_count = accepted_count
            )
         
        # 테스트 결과를 반환합니다.
        yield TestResult(
            test_result=0,
            code=code,
            language=language,
            testcase=testcase_result,
            code_length=len(code.encode('utf-8')),
            msg=msg,
            file_id=file_id
        )
        self.remove_file(file_id=file_id)

    # [채점 모드] 사용자의 코드를 채점합니다. 
    async def judge(self, code: str, language: str, problem_id: int, time_limit: float, memory_limit: int):
        # 해당 문제 아이디로 테스트케이스를 가져옵니다.
        testcase_count = await self.__testcase_service.get_testcase_count(problem_id=problem_id)

        # 파일을 만듭니다.
        file_id = self.make_file(code=code, language=language)

        yield PartialResult(
            status_code=1,
            message="컴파일 중..."
        )

        compile_result = await self.compile(language=language, file_id=file_id)

        # 컴파일 오류가 뜬 경우입니다.
        if compile_result["is_error"]:
            yield PartialResult(
                status_code=7,
                message="컴파일 오류"
            )
            yield JudgeResult(
                problem_id=problem_id,
                judge_result=4,
                code=code,
                language=language,
                code_length=len(code.encode('utf-8')),
                msg="Compile Error: {error_message}".format(error_message=compile_result["stderr"]),
                file_id=file_id
            )
            self.remove_file(file_id=file_id)
            return
        
        await self.__dummy_run_program(language, file_id)
        
        testcase_result = []
        execution_time = 0
        memory_usage = 0

        # 테스트를 시작합니다.
        for testcase_id in range(1, testcase_count + 1):
            testcase = await self.__testcase_service.get_testcase(problem_id=problem_id, testcase_id=testcase_id)

            # 프로그램을 실행합니다.
            test_result = await self.run_program(
                language=language,
                time_limit=time_limit,
                memory_limit=memory_limit,
                standard_input=testcase["input_data"],
                file_id=file_id
            )

            # 시간 초과 / 메모리 초과 / 런타임 오류가 뜬 경우입니다.
            if test_result["execution_result"]:
                execution_result_messages = {2: "시간 초과", 3: "메모리 초과", 5: "런타임 오류"}
                yield PartialResult(
                    status_code=test_result["execution_result"] + 3,
                    message=execution_result_messages[test_result["execution_result"]]
                )
                yield JudgeResult(
                    problem_id=problem_id,
                    judge_result=test_result["execution_result"],
                    code=code,
                    language=language,
                    code_length=len(code.encode('utf-8')),
                    msg=test_result["message"],
                    file_id=file_id
                )
                self.remove_file(file_id=file_id)
                return
            
            # 출력과 정답을 비교합니다.
            jury_result = self.compare_answer(test_result["stdout"], testcase["output_data"])

            judge_result = {
                "testcase_id": testcase_id,
                "is_passed": jury_result["is_accepted"],
                "message": jury_result["jury_result"],
                "execution_time": test_result["execution_time"],
                "memory_usage": test_result["memory_usage"]
            }

            yield PartialResult(
                status_code=2,
                message="채점 중... ({}%)".format(int(testcase_id * 100 / testcase_count)),
                data=judge_result
            )

            testcase_result.append(judge_result)

            execution_time = max(execution_time, test_result["execution_time"])
            memory_usage = max(memory_usage, test_result["memory_usage"])

            # 틀린 경우입니다.
            if not jury_result["is_accepted"]:
                yield PartialResult(
                    status_code=4,
                    message="오답입니다."
                )
                yield JudgeResult(
                    problem_id=problem_id,
                    judge_result=1,
                    code=code,
                    language=language,
                    testcase=testcase_result,
                    execution_time=execution_time,
                    memory_usage=memory_usage,
                    code_length=len(code.encode('utf-8')),
                    msg="[Wrong Answer] Testcase #{} Failed: {}".format(testcase_id, jury_result["jury_result"]),
                    file_id=file_id
                )
                self.remove_file(file_id=file_id)
                return
         
        # 정답인 경우입니다.
        yield PartialResult(
            status_code=3,
            message="정답입니다!"
        )
        yield JudgeResult(
            problem_id=problem_id,
            judge_result=0,
            code=code,
            language=language,
            testcase=testcase_result,
            execution_time=execution_time,
            memory_usage=memory_usage,
            code_length=len(code.encode('utf-8')),
            msg="[Accepted] All Testcases Passed!",
            file_id=file_id
        )
        self.remove_file(file_id=file_id)

    # 프로그램 파일을 만드는 함수입니다.
    def make_file(self, code: str, language: str) -> str:
        file_id = get_random_id()
        file_directory = f"{self.__code_file_base_dir}/{file_id}"

        # 디렉토리를 만듭니다.
        if not os.path.exists(file_directory):
            os.makedirs(file_directory)
        
        # 디렉토리 안에 프로그램 파일을 만듭니다.
        with open(f"{file_directory}/Solution.{language}", "w") as file:
            file.write(code)

        return file_id

    # 컴파일을 진행하는 함수입니다.
    async def compile(self, language: str, file_id: str):
        # 컴파일을 진행합니다.
        process = await asyncio.create_subprocess_shell(
            self.__compile_command[language].format(file_id=file_id),
            stderr=asyncio.subprocess.PIPE
        )
        _, stderr = await process.communicate()

        compile_result = {
            "code": process.returncode,
            "stderr": stderr.decode()
        }
        compile_result["is_error"] = compile_result["code"] != 0 or len(compile_result["stderr"]) > 0
        
        return compile_result
    
    # 파일을 제거합니다.
    def remove_file(self, file_id: str):
        # 파일 아이디에 해당하는 디렉토리를 삭제합니다.
        shutil.rmtree(f"{self.__code_file_base_dir}/{file_id}")
    
    # 리소스 준비를 위해 실행하는 더미 프로세스입니다.
    async def __dummy_run_program(self, language, file_id):
        process = await asyncio.create_subprocess_shell(
            self.__run_command[language].format(file_id=file_id),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        try:
            await asyncio.wait_for(process.communicate(), timeout=0.1)
        except asyncio.TimeoutError:
            return

    # 프로그램을 실행합니다.
    async def run_program(self, language: str, time_limit: float, memory_limit: int, standard_input: str, file_id: str):
        start_time = time.time()
        
        # 프로그램을 실행합니다.
        process = await asyncio.create_subprocess_shell(
            self.__run_command[language].format(file_id=file_id),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        memory_usage = []
        stdout, stderr = None, None

        # 실행 시간과 메모리 사용량을 모니터링하는 함수입니다.
        async def monitor():
            while process.returncode is None:
                try:
                    p = psutil.Process(process.pid)
                    mem_info = p.memory_info()
                    memory_usage.append(mem_info.rss / 1024)
                
                    if mem_info.rss / (1024 * 1024) > memory_limit:
                        raise MemoryError()
                
                    if time.time() - start_time > time_limit:
                        raise TimeoutError()

                    await asyncio.sleep(0.05)
                except MemoryError:
                    process.terminate()
                    raise MemoryError()
                except psutil.ZombieProcess:
                    return
                except TimeoutError:
                    process.terminate()
                    raise TimeoutError()
                except Exception:
                    return

        try:
            # 백그라운드에서 리소스 모니터링을 진행합니다.
            monitor_task = asyncio.create_task(monitor())

            stdout, stderr = await asyncio.wait_for(
                process.communicate(input=standard_input.encode()),
                timeout=time_limit
            )
            end_time = time.time()
            await monitor_task

        # 시간 초과가 난 경우입니다.
        except (asyncio.TimeoutError, TimeoutError):
            return {
                "execution_result": 2,
                "message": "Time Limit Exceed"
            }
        # 메모리 초과가 난 경우입니다.
        except MemoryError:
            return {
                "execution_result": 3,
                "message": "Memory Limit Exceed"
            }
        # 이외의 오류입니다.
        except Exception as e:
            return {
                "execution_result": 5,
                "message": "Runtime Error: {}".format(e)
            }

        # 런타임 오류가 난 경우입니다.
        if len(stderr.decode()) > 0:
            return {
                "execution_result": 5,
                "message": "Runtime Error: {}".format(stderr.decode())
            }

        # 실행 시간과 최대 메모리 사용량을 계산합니다.
        execution_time = int((end_time - start_time) * 1000)
        memory_usage = int(max(memory_usage))

        return {
            "execution_result": 0,
            "execution_time": execution_time,
            "memory_usage": memory_usage,
            "stdout": stdout.decode()
        }

    # 두 출력을 비교하는 함수입니다.
    def compare_answer(self, user_output: str, jury_output: str):
        user_output_lines = user_output.strip().split("\n")
        jury_output_lines = jury_output.strip().split("\n")

        is_accepted = True
        msg = ""

        token, line = 1, 1
        # 한 줄을 비교합니다.
        for i in range(len(jury_output_lines)):
            # 사용자의 출력 줄이 더 많은 경우 
            if i >= len(user_output_lines):
                msg = f"line {line}, {token}th token not matched"
                is_accepted = False
                break

            user_output_line = user_output_lines[i].strip().split()
            jury_output_line = jury_output_lines[i].strip().split()

            for j in range(len(jury_output_line)):
                # 사용자의 출력 토큰이 더 많은 경우
                if j >= len(user_output_line):
                    msg = f"line {line}, {token} th token not matched"
                    is_accepted = False
                    break

                user_token = user_output_line[j]
                jury_token = jury_output_line[j]

                # 토큰의 값이 다른 경우 
                if user_token != jury_token:
                    msg = f"line {line}, {token} th token not matched"
                    is_accepted = False
                    break

                token += 1
            
            # 틀린 경우입니다.
            if not is_accepted:
                break

            # 틀린 경우입니다.
            if len(jury_output_line) != len(user_output_line):
                msg = f"line {line}, {token} th token not exists"
                is_accepted = False
                break

            line += 1

        # 출력 초과가 난 경우입니다.
        if is_accepted and len(jury_output_lines) != len(user_output_lines):
            msg = f"line {line}, {token} th token not exists"
            is_accepted = False

        # 정답인 경우입니다.
        if is_accepted:
            msg = f"all {line} lines, {token} tokens all matched"
        
        return {
            "is_accepted": is_accepted,
            "jury_result": msg
        }

