# 달맹저지 채점서버 💻

##### · 사용자의 코드를 실행, 테스트, 채점할 수 있는 서버입니다.

</br>
## 서버 정보
* 프레임워크 : FastAPI
* 언어 / 버전 : Python 3.12

</br>
## 서버 실행하기 

1. 서버 실행을 위한 라이브러리를 설치합니다.</br>

`pip install -r requirements.txt`

2. 환경변수 파일을 작성합니다. </br>

`.env_template` 파일을 보고 `.env` 이름의 파일에 환경변수를 작성하면 됩니다.


| 환경변수 이름  | 설명 | 기본값 |
| ------------- | ------------- | ------------- |
| `JUDGE_SERVER_PORT`  | 서버의 포트 번호입니다.  | `8004`  |
| `LOG_DIRECTORY`  | 로그 파일이 저장될 디렉토리 경로입니다.  |  `./log` |
| `CHUNK_SIZE`  | 사용자의 파일을 테스트 · 실행 할 때, 묶어서 처리할 요청의 개수입니다.   | `6`  |
| `DEFAULT_TIME_LIMIT`  | 사용자의 파일을 테스트 · 실행 할 때, 적용되는 시간 제한입니다. (초, `float`)  | `5.0`  |
| `DEFAULT_MEMORY_LIMIT`  | 사용자의 파일을 테스트 · 실행 할 때, 적용되는 메모리 제한입니다. (MB, `int`)  | `128`  |


3. 서버를 실행합니다. </br>

`python Main.py`

아래와 같은 로그가 나오면 서버 실행에 성공한 것입니다.

```
INFO:     Started server process [40063]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8004 (Press CTRL+C to quit)
```


</br>

## 지원 언어와 형식


* 실행 언어는 현재 `Python`, `C`, `C++`, `Java`만 지원합니다.
* 달맹저지 채점 서버의 모든 입력은 <strong>표준 입력(Standard Input)</strong>, 모든 출력은 <strong>표준 출력(Standard Output)</strong> 으로 처리합니다.


* `Java` 언어에 대해 메인 클래스의 이름은 `Solution`이어야 하고, 메인 함수(`main`)가 있어야 합니다.
* `Java` 언어 기본 예시 :
```
import java.util.*;

class Solution {
    public static void main(String[] args){
        Scanner sc = new Scanner(System.in); // 표준 입력 Scanner 객체

		// 여기에 정답 코드를 작성해주세요.
    }
}
```


</br>

## 코드 채점 · 테스트 · 실행하기

* 본 문서에서는 대표적인 코드 채점 · 테스트 · 실행에 대해서만 설명합니다.</br>
* `/docs`에서 FastAPI가 제공하는 모든 API에 대한 명세를 볼 수 있습니다.



* 모든 기능은 HTTP 요청을 통해 이용합니다.
* 모든 응답은 `BaseResponse` 클래스에 의해 처리되며 동일한 구조를 갖고 있습니다.


* 응답 파라미터 설명

| 응답 파라미터 이름  | 타입 |설명 |
| ------------- | ------------- |------------- |
| `status_code`  | `Integer`  | 응답 상태 코드입니다. <br>`1XX`: Continue, `2XX`: Succeed, `4XX`: Exception · Error  |
| `msg`  | `String`  | 응답 결과 상태 메시지입니다.  |
| `data`  | `Optional[Object]`  | 응답 데이터입니다. |

* 응답 예시
```
{
	"status_code": 200,
    "msg": "succeed",
    "data": null
}
```


<hr>



#### 1. 코드 채점하기 

* 엔드포인트 : `/api/v1/judge`
* 요청 방식 : `POST`
* 요청 형식 : `application/json`
* 응답 형식 : `text/event-stream`

<hr>

* 요청 파라미터

| 요청 파라미터 이름  | 타입 |설명 |
| ------------- | ------------- |------------- |
| `problem_id`  | `Integer`  | 문제 번호입니다.  |
| `time_limit`  | `Float`  | 테스트케이스 당 프로세스 최대 실행 가능 시간입니다.  |
| `memory_limit`  | `Integer`  | 테스트케이스 당 프로세스 최대 가용 메모리입니다. |
| `language`  | `String`  | 실행할 코드의 언어 정보입니다.  |
| `code`  | `String`  | 실행할 코드입니다.  |
* `language`는 `"py"`, `"c"`, `"cpp"`, `"java"` 중에 하나여야 합니다.
* `time_limit`는 `10.0` 이하이어야 합니다.
* `memory_limit`는 `1024` 이하이어야 합니다.

</br>

* 요청 파라미터 예시
```
{
	"problem_id": 1,
	"time_limit": 1.0,
	"memory_limit": 64,
	"language": "py",
	"code": "print(\"Hello, {}!\".format(input()))",
}
```

* 응답 예시
```
// 채점 중간 결과 
{
	"status_code": 100,
    "msg": "succeed",
    "data": {
    	"status_code": 0,
        "message": "채점 대기 중...",
        "data": null
    }
}
{
	"status_code": 100,
    "msg": "succeed",
    "data": {
    	"status_code": 1,
        "message": "컴파일 중...",
        "data": null
    }
}
{
	"status_code": 100,
    "msg": "succeed",
    "data": {
    	"status_code": 2,
        "message": "채점 중... (1%)",
        "data": {
        	"testcase_id": 1,
            "is_passed": true,
            "message": "all 2 lines, 3 tokens all matched",
            "execution_time": 10,
            "memory_usage": 192
        }
    }
}
...
{
	"status_code": 100,
    "msg": "succeed",
    "data": {
    	"status_code": 3,
        "message": "정답입니다!",
        "data": null
    }
}

// 최종 채점 결과
{
	"status_code": 200,
    "msg": "succeed",
    "data" {
    	"problem_id": 1,
        "judge_result": 0,
        "code": "print(\"Hello, {}!\".format(input()))",
        "language": "py",
        "code_length": 35,
        "execution_time": 24, "memory_usage": 320,
        "testcase": [
        	{
            	"testcase_id": 1,
                "is_passed": true,
                "message": "all 2 lines, 3 tokens all matched",
                "execution_time": 10,
                "memory_usage": 192
            },
            ...
            {
            	"testcase_id": 100,
                "is_passed": true,
                "message": "all 2 lines, 3 tokens all matched",
                "execution_time": 23,
                "memory_usage": 224
            }
        ],
    	"msg": "[Accepted] All Testcases Passed!",
        "file_id": "0enklgtwt7wgwrjqh22e5vlknf4b6a"
    }
}
```
* 채점 중간 데이터에서 (`status_code = 100`인 경우) `data`의 `status_code`에 대한 정보는 아래와 같습니다.
	* `0`: 채점 대기 중인 상태입니다.
	* `1`: 프로그램을 컴파일 중입니다.
	* `2`: 프로그램을 실행 중인 상태입니다.
	* `3`: 정답
	* `4`: 오답
	* `5`: 시간 제한 초과
	* `6`: 메모리 제한 초과
	* `7`: 컴파일 오류
	* `8`: 런타임 오류 


* 채점 최종 데이터에서 `judge_result`에 대한 정보는 아래와 같습니다.
	* `0`: 정답 
	* `1`: 오답 
	* `2`: 시간 제한 초과
	* `3`: 메모리 제한 초과
	* `4`: 컴파일 오류
	* `5`: 런타임 오류 



<br>
<hr>


#### 2. 코드 테스트하기 

* 엔드포인트 : `/api/v1/test`
* 요청 방식 : `POST`
* 요청 형식 : `application/json`
* 응답 형식 : `text/event-stream`

<hr>

* 요청 파라미터

| 요청 파라미터 이름  | 타입 |설명 |
| ------------- | ------------- |------------- |
| `standard_ios`  | `List[Json]`  | 테스트 할 표준 입출력 데이터입니다.  |
| `language`  | `String`  | 실행할 코드의 언어 정보입니다.  |
| `code`  | `String`  | 실행할 코드입니다.  |
* `language`는 `"py"`, `"c"`, `"cpp"`, `"java"` 중에 하나여야 합니다.
* `standard_ios`는 두 개의 키, `"standard_input"`, `"expected_output"`가 있어야 합니다.
* `standard_ios`의 길이는 `10` 이하이어야 합니다.

</br>

* 요청 파라미터 예시
```
{
	"language": "py",
	"code": "print(\"Hello, {}!\".format(input()))",
    "standard_ios": [
    	{
        	"standard_input": "world",
            "expected_output": "Hello, world!"
        },
        {
        	"standard_input": "World",
            "expected_output": "Hello, World!"
        }
    ]
}
```

* 응답 예시
```
// 테스트 중간 결과 
{
	"status_code": 100,
    "msg": "succeed",
    "data": {
    	"status_code": 0,
        "message": "실행 대기 중...",
        "data": null
    }
}
{
	"status_code": 100,
    "msg": "succeed",
    "data": {
    	"status_code": 1,
        "message": "컴파일 중...",
        "data": null
    }
}
{
	"status_code": 100,
    "msg": "succeed",
    "data": {
    	"status_code": 3,
        "message": "테스트 성공!",
        "data": {
        	"testcase_id": 0,
            "is_passed": true,
            "message": "all 2 lines, 3 tokens all matched",
            "standard_output": "Hello, world!\n",
            "execution_time": 13,
            "memory_usage": 160
        }
    }
}
{
	"status_code": 100,
    "msg": "succeed",
    "data": {
    	"status_code": 3,
        "message": "테스트 성공!",
        "data": {
        	"testcase_id": 1,
            "is_passed": true,
            "message": "all 2 lines, 3 tokens all matched",
            "standard_output": "Hello, World!\n",
            "execution_time": 15,
            "memory_usage": 176
        }
    }
}

// 최종 테스트 결과
{
	"status_code": 200,
    "msg": "succeed",
    "data": {
    	"test_result": 0,
        "code": "print(\"Hello, {}!\".format(input()))",
        "language": "py",
        "code_length": 35,
        "testcase": [
        	{
            	"testcase_id": 0
                "is_passed": true,
                "message": "all 2 lines, 3 tokens all matched",
                "standard_output": "Hello, world!\n",
                "execution_time": 13,
                "memory_usage": 160
            },
            {
            	"testcase_id": 1,
                "is_passed": true,
                "message": "all 2 lines, 3 tokens all matched",
                "standard_output": "Hello, World!\n",
                "execution_time": 15,
                "memory_usage": 176
            }
        ],
        "msg": "모든 테스트를 성공했습니다!",
        "file_id": "tclc57p4pjlzdj4hy3as4xcdxjqjar"
    }
}
```
* 테스트 중간 데이터에서 (`status_code = 100`인 경우) `data`의 `status_code`에 대한 정보는 아래와 같습니다.
	* `0`: 채점 대기 중인 상태입니다.
	* `1`: 프로그램을 컴파일 중입니다.
	* `2`: 프로그램을 실행 중인 상태입니다.
	* `3`: 정답
	* `4`: 오답
	* `5`: 시간 제한 초과
	* `6`: 메모리 제한 초과
	* `7`: 컴파일 오류
	* `8`: 런타임 오류 

* 테스트 최종 데이터에서 `test_result`에 대한 정보는 아래와 같습니다.
	* `0`: 실행에 성공한 경우입니다. 
	    * 정답 / 오답 / 시간 제한 초과 / 메모리 제한 초과 / 런타임 오류를 모두 포함합니다.
	* `1`: 실행에 실패한 상태입니다.
        * 컴파일 과정에서 오류가 생긴 경우입니다.



<br>
<hr>


#### 3. 코드 실행하기 

* 엔드포인트 : `/api/v1/run`
* 요청 방식 : `POST`
* 요청 형식 : `application/json`
* 응답 형식 : `application/json`

<hr>

* 요청 파라미터

| 요청 파라미터 이름  | 타입 |설명 |
| ------------- | ------------- |------------- |
| `standard_input`  | `String`  | 프로그램 실행 시 프로세스에 전달한 표준 입력입니다.  |
| `language`  | `String`  | 실행할 코드의 언어 정보입니다.  |
| `code`  | `String`  | 실행할 코드입니다.  |
* `language`는 `"py"`, `"c"`, `"cpp"`, `"java"` 중에 하나여야 합니다.

</br>

* 요청 파라미터 예시
```
{
	"language": "py",
	"code": "print(\"Hello, {}!\".format(input()))",
    "standard_input": "world"
}
```

* 응답 예시
```
{
    "status_code": 200,
    "msg": "succeed",
    "data": {
        "run_result": 0,
        "code": "print(\"Hello, {}!\".format(input()))",
        "language": "py",
        "code_length": 35,
        "file_id": "n1gtdlfeecxurlf2si5m46peqdklid",
        "standard_input": "world",
        "standard_output": "Hello, world!\n",
        "execution_time": 11,
        "memory_usage": 208
    }
}
```
* `run_result`에 대한 정보는 아래와 같습니다.
	* `0`: 실행에 성공한 경우입니다.
	* `1`: 컴파일 오류
	* `2`: 시간 제한 초과 
	* `3`: 메모리 제한 초과 
	* `5`: 런타임 오류 

<br>

## 테스트케이스 추가하기 

테스트케이스 데이터는 `Testcases` 디렉토리 하에 존재합니다.
* `Testcases` 디렉토리 하에 문제 번호로 된 디렉토리를 만든 후, 그 안에 테스트케이스들을 넣습니다.
    * 만들고 싶은 문제의 번호가 `1`이라고 하면, `Testcases/1` 디렉토리를 만듭니다.


</br>

테스트케이스의 표준 입력 확장자는 `.in`, 표준 출력 확장자는 `.out`입니다.
* 테스트케이스의 파일 이름은 자연수로, 반드시 `1`부터 시작해야 하고, 순차적이어야 합니다.
* 한 테스트케이스 번호에는 항상 입력과 출력 파일이 모두 존재해야 합니다.
* 예시: `1.in`, `1.out`, `2.in`, `2.out`, ...

</br>

본 프로젝트 코드에서는 1번 문제에 대한 예시 테스트케이스를 제공합니다.
* `Testcases/1` 디렉토리를 참고해주세요.

</br>

## 서버 테스트하기  

본 프로젝트 코드에는 서버가 정상적으로 동작하는지 확인하고, API에 대한 이해를 위해 채점 / 테스트/ 실행에 대한 테스트 코드를 제공합니다.

* `Test/judge.py` : `1`번 문제에 대해 네 가지 언어(`"py"`, `"c"`, `"cpp"`, `"java"`)에 대한 채점 요청을 동시에 날립니다.
* `Test/test.py` : 네 가지 언어(`"py"`, `"c"`, `"cpp"`, `"java"`)에 대한 테스트 요청을 동시에 날립니다. 각 요청에는 테스트케이스가 4개 포함되어 있습니다.
* `Test/run.py` : 네 가지 언어(`"py"`, `"c"`, `"cpp"`, `"java"`)에 실행 채점 요청을 동시에 날립니다.

</hr>
</br>

<hr>

## Q1. `Hello, world!`

본 프로젝트 코드에서는 1번 문제에 대한 테스트케이스와 정답 코드를 제공합니다.
* 테스트케이스: `Testcases/1`
    * 본 문제는 100개의 테스트케이스로 이루어져 있습니다.
* 정답 코드: `Solution/1`

<hr>

#### [권장 리소스 제한]
* 시간 제한 : 모든 언어에서 1.0초
* 메모리 제한 : 모든 언어에서 64MB
* API 호출 시 상황에 맞게 변경할 수 있습니다.

#### [문제]
이름을 입력 받고 인사말을 출력해봅시다.

#### [입력]
첫 줄에 이름을 입력받습니다.

#### [출력]
첫 줄에 `Hello, {이름}!`형식으로 출력합니다.

#### [제한]
이름은 영어 알파벳과 숫자로만 이루어진 길이 10 이하의 문자열입니다.

#### [예시]
| 예시 번호  | 예시 표준 입력 | 예시 표준 출력  | 예시 설명 |
| ------------- | ------------- | ------------- | ------------- |
| 1  | `world`  | `Hello, world!`  | 이름이 `world`이므로 인사말은 `Hello, world!`입니다.  |
| 2  | `dalmeng`  | `Hello, dalmeng!`  | 이름이 `dalmeng`이므로 인사말은 `Hello, dalmeng!`입니다.  |



</br>

## 참고


* 과도한 리소스 사용을 막기 위해 달맹저지 서버의 `Scheduler` 클래스가 채점 · 테스트 · 실행 요청을 리소스 효율적으로 처리합니다.

#### [채점]
* 채점 요청은 <strong>한 번에 한 개</strong> 처리할 수 있습니다.
* 채점이 진행 중이지 않을 때, 채점 큐에서 2초 마다 채점 요청을 가져와 처리합니다.
* 즉, 한 채점 프로세스가 점유하는 최대 실행 시간은 `10`초, 메모리는 `1`GB입니다. 

#### [테스트 · 실행]

* 테스트 · 실행 요청은 <strong>한 번에 최대 여섯 개</strong> 처리할 수 있습니다.
* 배치 사이즈는 `.env` 파일의 `CHUNK_SIZE` 인자에서 변경할 수 있습니다.
* 한 프로세스가 점유하는 최대 실행 시간과 최대 메모리는 각각 `5.0`초, `128`MB입니다.
* 이 설정은 `.env` 파일의 `DEFAULT_TIME_LIMIT`와 `DEFAULT_MEMORY_LIMIT` 인자에서 변경할 수 있습니다.
* 즉, 한 배치 프로세스가 점유하는 최대 실행 시간은 `5.0`초, 메모리는 `768`MB입니다.

