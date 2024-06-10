from fastapi import FastAPI, Depends
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
import asyncio
import uvicorn

from Controller.TestcaseController import TestcaseController
from Scheduler.Scheduler import Scheduler
from Dto.Request.TestcaseInfoRequestDto import TestcaseInfoRequestDto
from Dto.Request.RunRequestDto import RunRequestDto
from Dto.Request.TestcaseRequestDto import TestcaseInfoRequestDto
from Dto.Request.JudgeRequestDto import JudgeRequestDto
from Dto.Request.TestRequestDto import TestRequestDto
from Dto.Response.BaseResponseDto import BaseResponseDto
from Exception.Exceptions import *
from Util.EnvironmentVariable import env

# 서버 실행 전, 스케줄러 메소드를 백그라운드에서 실행합니다.
@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.gather(
        *[
            Scheduler().judge_schedule(),
            Scheduler().run_schedule()
        ]
    )
    yield

app = FastAPI(lifespan=lifespan)
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
    except (ProblemNotFoundException or TestcaseNotFoundException) as e:
        return BaseResponseDto.failed(
            status_code=e.code,
            msg=e.msg
        )
    except Exception as e:
        return BaseResponseDto.failed(
            msg=str(e)
        )

# 문제를 채점합니다.
@app.post(base_endpoint + "/judge")
async def post_judge(judge_request_dto: JudgeRequestDto):
    return StreamingResponse(
        Scheduler().judge(
            task=judge_request_dto,
        )
    )
    
# 사용자의 코드를 테스트합니다.
@app.post(base_endpoint + "/test")
async def post_judge(test_request_dto: TestRequestDto):
    return StreamingResponse(
        Scheduler().test(
            task=test_request_dto
        )
    )
    
# 사용자의 코드를 실행합니다.
@app.post(base_endpoint + "/run")
async def post_judge(run_request_dto: RunRequestDto):
    try:
        run_result = await Scheduler().run(task=run_request_dto)
        return BaseResponseDto.ok(
            data=run_result
        )
    except (InvalidStandardInputException, TooLongOutputException) as e:
        return BaseResponseDto.failed(
            code=e.code,
            msg=e.msg
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
