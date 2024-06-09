# 커스텀 예외 클래스입니다.

# 문제가 존재하지 않는 경우
class ProblemNotFoundException(Exception):
    code: int = 404
    msg: str = "Problem not found"

# 테스트케이스가 존재하지 않는 경우
class TestcaseNotFoundException(Exception):
    code: int = 404
    msg: str = "Testcase not found"

# 채점 시 시간 제한은 10초 이내로 설정해야 합니다.
class InvalidTimeLimitException(Exception):
    code: int = 405
    msg: str = "Time limit can not exceed 10 seconds"

# 채점 시 메모리 제한은 1GB 이내로 설정해야 합니다.
class InvalidMemoryLimitException(Exception):
    code: int = 405
    msg: str = "Memory can not exceed 1024MB"

# 입력이 너무 길면 안 됩니다. (1KB 이하)
class InvalidStandardInputException(Exception):
    code: int = 405
    msg: str = "Input data size can not exceed 1KB"

# 예상 출력이 너무 길면 안 됩니다. (1KB 이하)
class InvalidExpectedOutputException(Exception):
    code: int = 405
    msg: str = "Expected output data size can not exceed 1KB"

# 프로그램 실행 시 표준 출력이 너무 길면 안 됩니다. (1KB 이하)
class TooLongOutputException(Exception):
    code: int = 405
    msg: str = "Execution standard output size can not exceed 1KB"

# 프로그램 테스트 시 테스트케이스의 개수는 최대 10개입니다.
class TooManyTestcasesException(Exception):
    code: int = 405
    msg: str = "The number of testcases can not exceed 10"