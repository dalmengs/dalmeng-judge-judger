import asyncio
import json

from Util.Singleton import Singleton
from Dto.Response.BaseResponseDto import BaseResponseDto
from Exception.Exceptions import *
from Controller.JudgeController import JudgeController
from Controller.RunController import RunController
from Controller.TestController import TestController
from Model.PartialResult import PartialResult
from Util.EnvironmentVariable import env

# 채점 / 실행 요청을 스케줄링하는 클래스입니다.
@Singleton
class Scheduler:
    __judge_queue = asyncio.Queue()
    __judge_task = False

    __run_queue = asyncio.Queue()
    __run_task = 0

    __judge_lock = asyncio.Lock()
    __run_lock = asyncio.Lock()

    __chunk_size = int(env("CHUNK_SIZE"))

    # 채점 요청을 처리합니다.
    async def judge(self, task):
        if task.time_limit > 10:
            yield json.dumps(
                BaseResponseDto.failed(
                    exception=InvalidTimeLimitException()
                )
            )
            return
        elif task.memory_limit > 1024:
            yield json.dumps(
                BaseResponseDto.failed(
                    exception=InvalidMemoryLimitException()
                )
            )
            return

        yield json.dumps(PartialResult(
            status_code=0,
            message="채점 대기 중..."
        ).to_dict(), ensure_ascii=False) + "\n"

        is_scheduled = asyncio.get_running_loop().create_future()
        await self.__add_judge(is_scheduled)

        await is_scheduled

        async for result in JudgeController().judge(task):
            yield result

        async with self.__judge_lock:
            self.__judge_task = False
    
    # 테스트 요청을 처리합니다.
    async def test(self, task):
        io = task.standard_ios
        if len(io) > 10:
            yield json.dumps(
                BaseResponseDto.failed(
                    exception=TooManyTestcasesException()
                )
            )
            return
        for o in io:
            si = o["standard_input"]
            so = o["expected_output"]
            if len(si.encode('utf-8')) > 1024:
                yield json.dumps(
                    BaseResponseDto.failed(
                        exception=InvalidStandardInputException()
                    )
                )
                return
            elif len(so.encode('utf-8')) > 1024:
                yield json.dumps(
                    BaseResponseDto.failed(
                        exception=InvalidExpectedOutputException()
                    )
                )
                return

        yield json.dumps(PartialResult(
            status_code=0,
            message="실행 대기 중..."
        ).to_dict(), ensure_ascii=False) + "\n"

        is_scheduled = asyncio.get_running_loop().create_future()
        await self.__add_run(is_scheduled)

        await is_scheduled

        async for result in TestController().test(task):
            yield result

        async with self.__run_lock:
            self.__run_task -= 1
    
    # 실행 요청을 처리합니다.
    async def run(self, task):
        if len(task.standard_input.encode('utf-8')) > 1024:
            raise InvalidStandardInputException()

        is_scheduled = asyncio.get_running_loop().create_future()
        await self.__add_run(is_scheduled)

        await is_scheduled

        result = await RunController().run(task)

        async with self.__run_lock:
            self.__run_task -= 1
        
        if len(result.get_standard_output().encode('utf-8')) > 1024:
            raise TooLongOutputException()

        return result

    # 채점 큐에 채점 요청을 추가합니다.
    async def __add_judge(self, future):
        async with self.__judge_lock:
            await self.__judge_queue.put(future)
        
    # 채점 큐로부터 요청을 스케줄링합니다.
    async def judge_schedule(self):
        while True:
            await asyncio.sleep(3)
            async with self.__judge_lock:
                if not self.__judge_task and self.__judge_queue.qsize():
                    self.__judge_task = True
                    task_future = await self.__judge_queue.get()
                    task_future.set_result(True)
                    print("채점을 시작합니다. - {}".format(task_future))

    # 실행 / 테스트 큐에 요청을 추가합니다.
    async def __add_run(self, future):
        async with self.__run_lock:
            await self.__run_queue.put(future)
    
    # 실행 / 테스트 큐로부터 요청을 스케줄링합니다.
    async def run_schedule(self):
        while True:
            await asyncio.sleep(2)

            async with self.__run_lock:
                if not self.__run_task and self.__run_queue.qsize():
                    t = []

                    while self.__run_queue.qsize():
                        self.__run_task += 1
                        task_future = await self.__run_queue.get()
                        task_future.set_result(True)

                        t.append(task_future)

                        if self.__run_task == self.__chunk_size:
                            break
                    
                    print("테스트 및 실행 요청을 처리 시작합니다. - {}".format(t))
