# 채점 중간 결과를 전달하는 객체입니다.
class PartialJudgeResult:
    # `status_code`는 0부터 3 사이의 정수입니다.
    # - 0: 채점 대기 중인 상태입니다.
    # - 1: 프로그램을 컴파일 중입니다.
    # - 2: 프로그램을 실행 중인 상태입니다.
    # - 3: 정답
    # - 4: 오답
    # - 5: 시간 초과
    # - 6: 메모리 초과 
    # - 7: 컴파일 에러 
    # - 8: 런타임 에러 
    def __init__(self, status_code, message):
        self.__status_code = status_code
        self.__message: str = message

    def get_status_code(self):
        return self.__status_code

    def get_message(self):
        return self.__message
    def to_dict(self):
        return {
            "status_code": self.__status_code,
            "message": self.__message
        }
