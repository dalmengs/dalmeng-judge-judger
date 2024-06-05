
class ProblemNotFoundException(Exception):
    code: int = 404
    msg: str = "Problem not found"

class TestcaseNotFoundException(Exception):
    code: int = 404
    msg: str = "Testcase not found"

class JudgeCompileError(Exception):
    code: int = 400
    msg: str = "Compile Error"