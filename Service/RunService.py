from Util.logger import log
from Util.Singleton import Singleton
from Judger.Judger import Judger

@Singleton
class RunService:
    
    __judger: Judger = Judger()

    # 사용자의 코드를 테스트합니다.
    async def run(self, code: str, language: str, standard_input: str):
        return await self.__judger.run(
            code=code,
            language=language,
            standard_input=standard_input
        )
    