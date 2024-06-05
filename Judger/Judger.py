#& Imports
import time
import psutil
import threading
import subprocess

from Util.Singleton import Singleton
from Service.TestcaseService import TestcaseService
from Model.JudgeResult import JudgeResult
from Model.PartialJudgeResult import PartialJudgeResult
from Exception.Exceptions import *

@Singleton
class Judger:

    __code_file_base_dir = "./Code"
    __testcase_service: TestcaseService = TestcaseService()

    __compile_command = {
        "cpp": "g++ ./Code/Solution.cpp -o ./Code/Solution -O2 -Wall -lm -std=gnu++17",
        "c": "gcc ./Code/Solution.c -o ./Code/Solution -O2 -Wall -lm -std=gnu11",
        "java": "javac -J-Xmx1024m -encoding UTF-8 ./Code/Solution.java",
        "py": "python3 -W ignore -c \"import py_compile; py_compile.compile(r'./Code/Solution.py')\""
    }
    __run_command = {
        "cpp": "./Code/Solution",
        "c": "./Code/Solution",
        "java": "java -Dfile.encoding=UTF-8 ./Code/Solution",
        "py": "python3 -W ignore ./Code/Solution.py"
    }

    # 사용자의 코드를 채점합니다. 
    async def judge(self, code: str, language: str, problem_id: int, time_limit: float, memory_limit: int):

        # 채점 대기 중 사인을 보냅니다.
        yield PartialJudgeResult(
            status_code=0,
            message="채점 대기 중..."
        )

        # 문제 아이디에 해당하는 문제가 있는지 확인하고, 테스트케이스의 개수를 구합니다.
        testcase_count = await self.__testcase_service.get_testcase_count(
            problem_id=problem_id
        )

        # 파일을 만들고 파일 이름을 가져옵니다.
        self.make_file(
            code=code,
            language=language
        )

        # 컴파일 중 사인을 보냅니다.
        yield PartialJudgeResult(
            status_code=1,
            message="컴파일 중..."
        )
        # 컴파일을 합니다.
        compile_result = self.compile(
            language=language
        )

        # 컴파일 오류가 난 경우 
        if compile_result["is_error"]:
            # 채점 종료(컴파일 에러) 사인을 보냅니다.
            yield PartialJudgeResult(
                status_code=7,
                message="컴파일 에러"
            )
            # 채점 결과를 반환합니다.
            yield JudgeResult(
                problem_id=problem_id,
                judge_result=4, # 컴파일 오류 
                code=code,
                language=language,
                code_length=len(code.encode('utf-8')),
                msg="Compile Error: {error_message}".format(
                    error_message=compile_result["stderr"]
                )
            )
            return
        
        testcase_result = []
        execution_time = 0
        memory_usage = 0

        for testcase_id in range(1, testcase_count + 1):
            # 채점 중 사인을 보냅니다.
            yield PartialJudgeResult(
                status_code=2,
                message="채점 중... ({}%)".format(int(testcase_id * 100 / testcase_count))
            )

            # 테스트케이스를 가져옵니다.
            testcase = await self.__testcase_service.get_testcase(
                problem_id=problem_id,
                testcase_id=testcase_id
            )

            # 테스트케이스로 프로그램을 테스트합니다.
            test_result = self.run_program(
                language=language,
                time_limit=time_limit,
                memory_limit=memory_limit,
                standard_input=testcase["input_data"]
            )

            # 시간 초과 / 메모리 초과 / 런타임 에러 
            if test_result["execution_result"]:
                execution_result_messages = {2: "시간 초과", 3: "메모리 초과", 5: "런타임 에러"}
                # 채점 중 오류 사인을 보냅니다.
                yield PartialJudgeResult(
                    status_code=test_result["execution_result"] + 3,
                    message=execution_result_messages[test_result["execution_result"]]
                )
                # 채점 결과를 반환합니다.
                yield JudgeResult(
                    problem_id=problem_id,
                    judge_result=test_result["execution_result"],
                    code=code,
                    language=language,
                    code_length=len(code.encode('utf-8')),
                    msg=test_result["message"]
                )
                return
            
            # 실행이 정상적으로 끝났으므로 답을 비교합니다.
            jury_result = self.compare_answer(
                test_result["stdout"],
                testcase["output_data"]
            )

            # 테스트 결과를 저장합니다.
            testcase_result.append({
                "testcase_id": testcase_id,
                "is_passed": jury_result["is_accepted"],
                "message": jury_result["jury_result"],
                "execution_time": test_result["execution_time"],
                "memory_usage": test_result["memory_usage"]
            })

            # 실행 시간과 메모리 사용량을 갱신합니다.
            execution_time = max(execution_time, test_result["execution_time"])
            memory_usage = max(memory_usage, test_result["memory_usage"])

            # 오답
            if not jury_result["is_accepted"]:
                # 오답 사인을 보냅니다.
                yield PartialJudgeResult(
                    status_code=4,
                    message="오답입니다."
                )
                # 채점 결과를 반환합니다.
                yield JudgeResult(
                    problem_id=problem_id,
                    judge_result=1,
                    code=code,
                    language=language,
                    testcase=testcase_result,
                    execution_time=execution_time,
                    memory_usage=memory_usage,
                    code_length=len(code.encode('utf-8')),
                    msg="[Wrong Answer] Testcase #{} Failed: {}".format(testcase_id, jury_result["jury_result"])
                )
                return
         
        # 정답 사인을 보냅니다.
        yield PartialJudgeResult(
            status_code=3,
            message="정답입니다!"
        )
        # 채점 결과를 반환합니다.
        yield JudgeResult(
            problem_id=problem_id,
            judge_result=0,
            code=code,
            language=language,
            testcase=testcase_result,
            execution_time=execution_time,
            memory_usage=memory_usage,
            code_length=len(code.encode('utf-8')),
            msg="[Accepted] All Testcases Passed!"
        )

    # 프로그램 파일을 만듭니다.
    def make_file(self, code: str, language: str):
        file = open(f"{self.__code_file_base_dir}/Solution.{language}", "w")
        file.write(code)
        file.close()

    # 파일을 컴파일합니다.
    def compile(self, language: str):
        p = subprocess.Popen(
            self.__compile_command[language],
            stderr=subprocess.PIPE,
            shell=True
        )
        (stdout, stderr) = p.communicate()

        compile_result = {
            "code": p.poll(),
            "stderr": stderr.decode()
        }
        compile_result["is_error"] = compile_result["code"] != 0 or len(compile_result["stderr"]) > 0
        
        return compile_result
    
    # 파일을 실행합니다.
    def run_program(self, language: str, time_limit: float, memory_limit: int, standard_input: str):
        start_time = time.time()
        
        # 프로그램을 실행합니다.
        process = subprocess.Popen(
            args=self.__run_command[language],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True
        )
        
        memory_usage = []
        stdout, stderr = None, None

        # 실행 시간과 메모리 사용량을 모니터링합니다.
        def monitor():
            try:
                while process.poll() is None:
                    p = psutil.Process(process.pid)
                    mem_info = p.memory_info()
                    memory_usage.append(mem_info.rss / 1024)
                    
                    # 메모리 사용량을 체크하고, 메모리 제한을 넘었으면 프로세스를 중단시킵니다.
                    if mem_info.rss / 1024 > memory_limit * 1024:
                        process.terminate()
                        raise MemoryError()
                    
                    # 실행 시간을 확인하고, 시간 제한을 넘었으면 프로세스를 중단시킵니다.
                    if time.time() - start_time > time_limit:
                        process.terminate()
                        raise TimeoutError()

                    # 0.05초 주기로 확인합니다.
                    time.sleep(0.05)
            except MemoryError:
                pass
            except TimeoutError:
                pass

        monitor_thread = threading.Thread(target=monitor)
        monitor_thread.start()

        try:
            stdout, stderr = process.communicate(input=standard_input.encode(), timeout=time_limit)
            monitor_thread.join()  # 모니터링 스레드가 끝날 때까지 기다립니다.

        except subprocess.TimeoutExpired: # 시간 초과 
            process.terminate()
            monitor_thread.join()
            return {
                "execution_result": 2,
                "message": "Time Limit Exceed"
            }
        
        except TimeoutError: # 시간 초과 
            process.terminate()
            monitor_thread.join()
            return {
                "execution_result": 2,
                "message": "Memory Limit Exceed"
            }
        
        except MemoryError: # 메모리 초과 
            process.terminate()
            monitor_thread.join()
            return {
                "execution_result": 3,
                "message": "Memory Limit Exceed"
            }
        except Exception as e: # 런타임 에러 
            process.terminate()
            monitor_thread.join()
            return {
                "execution_result": 5,
                "message": "Runtime Error: {}".format(e)
            }

        # 런타임 에러 
        if len(stderr.decode()) > 0:
            return {
                "execution_result": 5,
                "message": "Runtime Error: {}".format(stderr.decode())
            }

        end_time = time.time()

        # 실행 시간 / 메모리 사용량 
        execution_time = int((end_time - start_time) * 1000)
        memory_usage = int(max(memory_usage))

        return {
            "execution_result": 0,
            "execution_time": execution_time,
            "memory_usage": memory_usage,
            "stdout": stdout.decode()
        }

    def compare_answer(self, user_output: str, jury_output: str):
        user_output_lines = user_output.strip().split("\n")
        jury_output_lines = jury_output.strip().split("\n")

        is_accepted = True
        msg = ""

        token, line = 1, 1
        # 한 줄씩 비교합니다.
        for i in range(len(jury_output_lines)):
            if i >= len(user_output_lines):
                # 사용자의 출력 중 i번째 줄이 존재하지 않는 경우 
                msg = f"line {line}, {token}th token not matched"
                is_accepted = False
                break

            user_output_line = user_output_lines[i].strip().split()
            jury_output_line = jury_output_lines[i].strip().split()

            # 각 토큰을 비교합니다.
            for j in range(len(jury_output_line)):
                if j >= len(user_output_line):
                    # 사용자의 출력 i번째 줄 중에서 j번째 토큰이 존재하지 않는 경우 
                    msg = f"line {line}, {token} th token not matched"
                    is_accepted = False
                    break

                user_token = user_output_line[j]
                jury_token = jury_output_line[j]

                # 두 토큰이 일치하지 않는 경우 
                if user_token != jury_token:
                    msg = f"line {line}, {token} th token not matched"
                    is_accepted = False
                    break

                token += 1
            
            if not is_accepted:
                break

            # 사용자의 출력 토큰이 더 많은 경우 
            if len(jury_output_line) != len(user_output_line):
                msg = f"line {line}, {token} th token not exists"
                is_accepted = False
                break

            line += 1

        # 사용자의 출력 줄 개수가 더 많은 경우 
        if is_accepted and len(jury_output_lines) != len(user_output_lines):
            msg = f"line {line}, {token} th token not exists"
            is_accepted = False

        # 모든 토큰이 일치하는 경우 
        if is_accepted:
            msg = f"all {line} lines, {token} tokens all matched"
        
        return {
            "is_accepted": is_accepted,
            "jury_result": msg
        }

