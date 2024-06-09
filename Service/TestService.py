import colorama
from colorama import Fore, Style

from Util.logger import log
from Util.Singleton import Singleton
from Judger.Judger import Judger
from Model.PartialResult import PartialResult

colorama.init(autoreset=True)

@Singleton
class TestService:
    
    __judger: Judger = Judger()

    # 사용자의 코드를 테스트합니다.
    async def test(self, code: str, language: str, standard_ios: list):
        async for test_result in self.__judger.test(
            code=code,
            language=language,
            standard_ios=standard_ios
        ):
            yield test_result
    