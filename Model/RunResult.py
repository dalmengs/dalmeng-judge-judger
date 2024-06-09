# 실행 결과를 담는 객체입니다.
class RunResult:
    # `run_result`는 0부터 5 사이의 정수입니다.
    # - 0: 실행 성공한 경우입니다.
    # - 1: Compile Error
    # - 2: Time Limit Exceed
    # - 3: Memory Limit Exceed
    # - 5: Runtime Error
    # `execution_time`의 단위는 ms입니다.
    # `memory_usage`의 단위는 KB입니다.
    def __init__(self, run_result, code, language, code_length, file_id, standard_input, standard_output, execution_time=None, memory_usage=None):
        self.__run_result: int = run_result
        self.__code: str = code
        self.__language: str = language
        self.__code_length: int = code_length
        self.__standard_input: list = standard_input
        self.__standard_output: list = standard_output
        self.__execution_time: int = execution_time
        self.__memory_usage: int = memory_usage
        self.__file_id: str = file_id
    
    def get_standard_output(self):
        return self.__standard_output

    def to_dict(self):
        return {
            "run_result": self.__run_result,
            "code": self.__code,
            "language": self.__language,
            "code_length": self.__code_length,
            "file_id": self.__file_id,
            "standard_input": self.__standard_input,
            "standard_output": self.__standard_output,
            "execution_time": self.__execution_time,
            "memory_usage": self.__memory_usage
        }
