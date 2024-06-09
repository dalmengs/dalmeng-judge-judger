# 실행 결과를 담는 객체입니다.
class TestResult:
    # `test_result`는 0 또는 1입니다.
    # - 0: 실행에 성공한 경우입니다. (정답 / 오답 / 시간 초과 / 메모리 초과 / 런타임 오류)
    # - 1: 실행에 실패한 경우입니다. (컴파일 오류)
    def __init__(self, test_result, code, language, code_length, file_id, testcase=None, msg=None):
        self.__test_result: int = test_result
        self.__code: str = code
        self.__language: str = language
        self.__code_length: int = code_length
        self.__testcase: list = testcase
        self.__msg: str = msg
        self.__file_id: str = file_id

    def to_dict(self):
        return {
            "test_result": self.__test_result,
            "code": self.__code,
            "language": self.__language,
            "code_length": self.__code_length,
            "testcase": self.__testcase,
            "msg": self.__msg,
            "file_id": self.__file_id
        }
