# 채점 결과를 담는 객체입니다.
class JudgeResult:
    # `judge_result`는 0부터 5 사이의 정수입니다.
    # - 0: Accepted
    # - 1: Wrong
    # - 2: Time Limit Exceed
    # - 3: Memory Limit Exceed
    # - 4: Compile Error
    # - 5: Runtime Error
    # `execution_time`의 단위는 ms입니다.
    # `memory_usage`의 단위는 KB입니다.
    def __init__(self, problem_id, judge_result, code, language, code_length, file_id, execution_time=None, memory_usage=None, testcase=None, msg=None):
        self.__problem_id: int = problem_id
        self.__judge_result: int = judge_result
        self.__code: str = code
        self.__language: str = language
        self.__code_length: int = code_length
        self.__execution_time: int = execution_time
        self.__memory_usage: int = memory_usage
        self.__testcase: list = testcase
        self.__file_id: str = file_id
        self.__msg: str = msg

    def to_dict(self):
        return {
            "problem_id": self.__problem_id,
            "judge_result": self.__judge_result,
            "code": self.__code,
            "language": self.__language,
            "code_length": self.__code_length,
            "execution_time": self.__execution_time,
            "memory_usage": self.__memory_usage,
            "testcase": self.__testcase,
            "msg": self.__msg,
            "file_id": self.__file_id
        }
