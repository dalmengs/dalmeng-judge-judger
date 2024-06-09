import json
from Util.Singleton import Singleton
from Service.JudgeService import JudgeService
from Dto.Response.BaseResponseDto import BaseResponseDto
from Model.JudgeResult import JudgeResult
from Dto.Request.JudgeRequestDto import JudgeRequestDto

@Singleton
class JudgeController:
    
    __judge_service: JudgeService = JudgeService()

    # 문제를 채점합니다.
    async def judge(self, judge_request_dto: JudgeRequestDto):
        async for judge_result in self.__judge_service.judge(
            code=judge_request_dto.code,
            language=judge_request_dto.language,
            problem_id=judge_request_dto.problem_id,
            time_limit=judge_request_dto.time_limit,
            memory_limit=judge_request_dto.memory_limit
        ):
            if isinstance(judge_result, JudgeResult):
                yield (json.dumps(
                    BaseResponseDto.ok(
                        data=judge_result.to_dict()
                    ), ensure_ascii=False
                ) + "\n")
            else:
                yield (json.dumps(
                    BaseResponseDto.ok(
                        status_code=100,
                        data=judge_result.to_dict()
                    ), ensure_ascii=False
                ) + "\n")

    