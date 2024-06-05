#& Imports
import os

from Util.Singleton import Singleton
from Service.JudgeService import JudgeService
from Dto.Request.JudgeRequestDto import JudgeRequestDto

@Singleton
class JudgeController:
    
    __judge_service: JudgeService = JudgeService()

    # 문제를 채점합니다.
    async def judge(self, judge_request_dto: JudgeRequestDto) -> int:
        return await self.__judge_service.judge(
            code=judge_request_dto.code,
            language=judge_request_dto.language,
            problem_id=judge_request_dto.problem_id,
            time_limit=judge_request_dto.time_limit,
            memory_limit=judge_request_dto.memory_limit
        )
    