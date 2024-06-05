from fastapi import FastAPI, Depends
import uvicorn

from Controller.TestcaseController import TestcaseController
from Controller.JudgeController import JudgeController
from Dto.Request.TestcaseInfoRequestDto import TestcaseInfoRequestDto
from Dto.Request.TestcaseRequestDto import TestcaseInfoRequestDto
from Dto.Request.JudgeRequestDto import JudgeRequestDto
from Dto.Response.BaseResponseDto import BaseResponseDto
from Exception.Exceptions import *
from Util.EnvironmentVariable import env

app = FastAPI(lifespan=None)
base_endpoint = "/api/v1"

# 특정 문제의 테스트케이스의 정보를 반환합니다.
@app.get(base_endpoint + "/testcase_info")
async def get_testcase_info(testcase_info_request_dto: TestcaseInfoRequestDto = Depends()) -> BaseResponseDto:
    try:
        testcase_info = await TestcaseController().get_testcase_info(
            testcase_info_request_dto=testcase_info_request_dto
        )
        return BaseResponseDto.ok(
            data=testcase_info
        )
    except ProblemNotFoundException as e:
        return BaseResponseDto.failed(
            status_code=ProblemNotFoundException.code,
            msg=ProblemNotFoundException.msg
        )
    except Exception as e:
        return BaseResponseDto.failed(
            msg=str(e)
        )

# 특정 문제의 테스트케이스를 반환합니다.
@app.get(base_endpoint + "/testcase")
async def get_testcase_info(testcase_reqeust_dto: TestcaseInfoRequestDto = Depends()) -> BaseResponseDto:
    try:
        testcase = await TestcaseController().get_testcase(
            testcase_reqeust_dto=testcase_reqeust_dto
        )
        return BaseResponseDto.ok(
            data=testcase
        )
    except ProblemNotFoundException as e:
        return BaseResponseDto.failed(
            status_code=ProblemNotFoundException.code,
            msg=ProblemNotFoundException.msg
        )
    except TestcaseNotFoundException as e:
        return BaseResponseDto.failed(
            status_code=TestcaseNotFoundException.code,
            msg=TestcaseNotFoundException.msg
        )
    except Exception as e:
        return BaseResponseDto.failed(
            msg=str(e)
        )

# 문제를 채점합니다.
@app.post(base_endpoint + "/judge")
async def post_judge(judge_request_dto: JudgeRequestDto) -> BaseResponseDto:
    try:
        judge_result = await JudgeController().judge(judge_request_dto)
        return BaseResponseDto.ok(
            data=judge_result
        )
    except Exception as e:
        return BaseResponseDto.failed(
            msg=str(e)
        )

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(env("JUDGE_SERVER_PORT"))
    )
