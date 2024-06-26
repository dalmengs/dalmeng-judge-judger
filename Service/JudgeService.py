import colorama
from colorama import Fore, Style

from Util.logger import log
from Util.Singleton import Singleton
from Judger.Judger import Judger
from Model.PartialResult import PartialResult

colorama.init(autoreset=True)

@Singleton
class JudgeService:
    
    __judger: Judger = Judger()

    # 문제를 채점합니다.
    async def judge(self, code: str, language: str, problem_id: int, time_limit: float, memory_limit: int):
        self.__judge_info(code, language, problem_id, time_limit, memory_limit)
        async for judge_result in self.__judger.judge(
            code=code,
            language=language,
            problem_id=problem_id,
            time_limit=time_limit,
            memory_limit=memory_limit
        ):
            self.__judge_result(judge_result)
            yield judge_result
    
    # 채점 정보를 출력합니다.
    def __judge_info(self, code, language, problem_id, time_limit, memory_limit):
        print(f"==================== [채점 정보] ====================")
        print(f"문제 번호: {problem_id}")
        print(f"언어: {language}")
        print(f"시간 제한: {time_limit}초")
        print(f"메모리 제한: {memory_limit}MB")
        print(f"제출 코드\n\n{code}\n")
        print(f"==================== [채점 현황] ====================")

    # 채점 결과를 출력합니다.
    def __judge_result(self, judge_result: PartialResult):
        if isinstance(judge_result, PartialResult):
        # 상태 코드에 따른 색깔 설정
            status_code = judge_result.get_status_code()
            if status_code == 0:
                color = Fore.BLUE
            elif status_code in [1, 2]:
                color = Fore.YELLOW
            elif status_code == 3:
                color = Fore.GREEN
            elif status_code == 4:
                color = Fore.RED
            elif status_code in [5, 6]:
                color = Fore.MAGENTA
            elif status_code in [7, 8]:
                color = Fore.CYAN
            else:
                color = Fore.WHITE

            # 색상을 적용하여 로그 출력
            print(f"{color}{judge_result.get_message()}{Style.RESET_ALL}")
        else:
            judge_result = judge_result.to_dict()
            print(f"==================== [채점 결과] ====================")
            status_code = judge_result["judge_result"]
            msg = ""
            if status_code == 0:
                color = Fore.GREEN
                msg = "정답입니다!"
            elif status_code == 1:
                color = Fore.RED
                msg = "틀렸습니다."
            elif status_code in [2, 3]:
                color = Fore.MAGENTA
                if status_code == 2: msg = "시간 초과"
                else: msg = "메모리 초과"
            elif status_code in [4, 5]:
                color = Fore.CYAN
                if status_code == 4: msg = "컴파일 에러"
                else: msg = "런타임 에러"
            print(f"최종 채점 결과: {color}{msg}{Style.RESET_ALL}")
            if judge_result["execution_time"]:
                print(f"실행 시간: {judge_result['execution_time']} ms")
            if judge_result["memory_usage"]:
                print(f"사용 메모리: {judge_result['memory_usage']} KB")
            print(f"코드 길이: {judge_result['code_length']} B")
            print(f"채점 결과: {judge_result['msg']}")
            testcase_string = ""
            if judge_result["testcase"]:
                for i in judge_result["testcase"]:
                    testcase_string += "[테스트케이스 {}] {} ({} ms, {} KB, '{}')\n".format(
                        i["testcase_id"],
                        "정답입니다!" if i["is_passed"] else "오답입니다.",
                        i["execution_time"],
                        i["memory_usage"],
                        i["message"]
                    )
            print("테스트케이스 세부 결과:\n{}".format(testcase_string.strip()))
            print(f"=====================================================")