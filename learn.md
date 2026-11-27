# 학습 위키

새 질의마다 질문을 소제목으로 추가합니다. 각 항목에는 핵심 설명, 실행 가능한 예시, 예시의 결과와 프로젝트에서의 적용을 정리합니다.

## "`scenario.json`의 `user_id`를 현재 사용자로 어떻게 적용하지?"

`scenario.json`을 읽어 반환하는 `support.load_data()`를 사용합니다. 반환된 데이터에서 `user_id`와 자료 목록을 꺼내 선택 함수에 전달하면 됩니다.

```python
data = support.load_data()
user_id = data["user_id"]
context = data["context"]

selected = select_context(context, user_id, now)
```

예를 들어 JSON의 `user_id`가 `"minji"`이면 `select_context`에는 `"minji"`가 전달됩니다. 함수가 `user_id`를 이미 인자로 받았다면 그 함수 안에서 JSON 파일을 다시 읽지 않습니다. 읽기와 필터링 책임을 분리하면 함수의 입력과 동작을 검사하기 쉽습니다.

## "JSON에서 읽은 사용자 ID와 자료의 값은 어떻게 비교하지?"

`==`는 값을 비교하고 `is`는 두 변수가 같은 객체인지 비교합니다. 사용자 ID 같은 문자열은 `==`로 비교합니다.

```python
user_id = "minji"
item = {"user_id": "minji"}

item["user_id"] == user_id      # True: 문자열 값이 같음
item["user_id"] == "public"     # False: 공개 자료는 아님
item["user_id"] is None         # False: None인지 확인할 때는 is 사용 가능
```

자료를 공개 또는 현재 사용자 소유인 경우에만 선택하는 조건은 다음과 같습니다.

```python
item["user_id"] == "public" or item["user_id"] == user_id
```

만료일이 `YYYY-MM-DD`처럼 같은 형식의 ISO 날짜 문자열이면 문자열끼리 비교할 수 있습니다. 이 형식은 연도부터 큰 단위 순으로 정렬되어 있어 날짜 순서와 문자열 순서가 일치합니다.

```python
expires_at = "2026-12-04"
now = "2026-12-03"

expires_at > now  # True: 만료일 전
expires_at > "2026-12-04"  # False: 만료일 당일부터 제외
```

형식이 다르거나 시간대가 포함된 날짜는 문자열로 비교하지 말고 날짜/시간 자료형으로 파싱합니다.

## "`history` 리스트를 딕셔너리로 바꿔야 하나?"

아니요. 이 코드에서 `history`는 메시지 딕셔너리들을 담은 리스트이고, 최종 메시지도 딕셔너리 여러 개를 담은 리스트여야 합니다.

```python
history = [
    {"role": "user", "content": "질문"},
    {"role": "assistant", "content": "응답"},
]

messages = [
    {"role": "developer", "content": "고정 지시"},
    *history,
    {"role": "user", "content": "새 질문"},
]
```

`*history`가 기존 리스트의 요소들을 새 리스트에 차례로 넣습니다. 결과의 `role` 순서는 `developer`, `user`, `assistant`, `user`입니다.

다음 표현은 리스트가 아니라 생성기를 만듭니다.

```python
(message for message in history)
```

리스트 안에 생성기의 요소를 넣으려면 `*(message for message in history)`처럼 펼칠 수 있습니다. 이미 리스트인 `history`라면 `*history`가 간단합니다. 중괄호 `{...}`를 쓰면 리스트가 아니라 딕셔너리 또는 집합을 만들기 때문에, 메시지 목록을 만들 때는 대괄호 `[...]`를 사용합니다.

## "`*`와 `**`는 어떻게 다르지?"

`*`는 리스트나 튜플 같은 반복 가능한 값의 요소를 펼칩니다. `**`는 딕셔너리 같은 매핑의 키-값을 펼칩니다.

```python
values = [1, 2]
combined = [0, *values, 3]
print(combined)  # [0, 1, 2, 3]
```

함수 호출에서는 `*`가 위치 인자, `**`가 키워드 인자로 전달됩니다.

```python
def describe(name, age):
    return f"{name}: {age}"

args = ["Minji", 20]
kwargs = {"name": "Minji", "age": 20}

describe(*args)   # describe("Minji", 20)
describe(**kwargs)  # describe(name="Minji", age=20)
```

딕셔너리 리터럴에서 `**`를 사용하면 딕셔너리를 합칠 수 있습니다. 같은 키가 있으면 뒤에 펼친 딕셔너리의 값이 우선합니다.

```python
defaults = {"timeout": 5, "retries": 1}
overrides = {"timeout": 10}
settings = {**defaults, **overrides}
print(settings)  # {"timeout": 10, "retries": 1}
```

함수 정의에서 `*args`는 추가 위치 인자들을 튜플로 모으고 `**kwargs`는 추가 키워드 인자들을 딕셔너리로 모읍니다. `history`는 리스트이므로 메시지 목록에 넣을 때 `*history`를 사용합니다.

## "`copy.deepcopy()`는 어떻게 사용하지?"

`copy.deepcopy(value)`는 객체와 그 안에 포함된 가변 객체들까지 재귀적으로 복사합니다. 복사본의 중첩된 리스트나 딕셔너리를 바꿔도 원본에는 영향이 없습니다.

```python
import copy

original = {
    "user_id": "minji",
    "metadata": {"active": True},
    "tags": ["study"],
}
copied = copy.deepcopy(original)

copied["metadata"]["active"] = False
copied["tags"].append("python")

print(original["metadata"]["active"])  # True
print(original["tags"])                # ["study"]
```

얕은 복사인 `copy.copy()`는 바깥 객체만 복사합니다. 안쪽 딕셔너리와 리스트는 원본과 복사본이 함께 참조할 수 있습니다.

```python
import copy

shallow = copy.copy(original)
shallow["metadata"]["active"] = False

print(original["metadata"]["active"])  # False: 중첩 딕셔너리는 공유됨
```

이 프로젝트의 자료는 중첩 딕셔너리이므로 `select_context()`에서 선택한 항목을 `copy.deepcopy(item)`으로 복사하면, 호출자가 결과를 수정해도 입력 자료가 바뀌지 않습니다.

```python
selected_item = copy.deepcopy(item)
selected_item["body"] = "수정된 본문"
# item["body"] 값은 그대로 유지
```

## "기억 조회·저장에 반환할 별도 object 변수가 있을까?"

Python에 기억 전용 `object`나 특별한 반환 변수는 없습니다. 이 코드에서는 `records`가 기억 저장소이고, 각 기억은 딕셔너리입니다. `key`는 `minji:style`처럼 사용자와 기억 이름을 결합하고, `value`는 저장할 기억 데이터입니다.

```python
records = {}
key = "minji:style"
value = {"text": "짧은 한국어 설명", "expires_at": "2026-12-04"}

records[key] = copy.deepcopy(value)  # 저장
record = records.get(key)            # 조회; 없으면 None
result = copy.deepcopy(record)       # 호출자에게 돌려줄 사본
```

`record`나 `result`는 가독성을 위한 일반 변수 이름입니다. 꼭 별도 변수에 담을 필요 없이 바로 반환해도 됩니다.

```python
if action == "read":
    return copy.deepcopy(records.get(key))
```

조회 결과가 없으면 `records.get(key)`는 `None`을 반환합니다. 저장할 때도 `copy.deepcopy(value)`를 사용하면 호출자가 원래 전달한 딕셔너리를 나중에 수정해도 저장소 값이 바뀌지 않습니다. 조회 결과 역시 사본으로 반환하면 호출자가 결과를 수정해도 저장된 기억이 유지됩니다.

## "딕셔너리에서 항목을 어떻게 삭제하지?"

`del records[key]`은 항목을 삭제하지만, key가 없으면 `KeyError`가 발생합니다. 없는 key도 오류 없이 처리하려면 `pop(key, default)`를 사용합니다. 두 번째 인수 `None`은 key가 없을 때 반환할 기본값입니다.

```python
records = {"minji:style": {"text": "간단히 설명"}}

deleted = records.pop("minji:style", None)
missing = records.pop("minji:task", None)

print(deleted)  # {"text": "간단히 설명"}
print(missing)  # None
print(records)  # {}
```

`memory_action()`에서는 key가 `f"{user_id}:{name}"`이므로 `records.pop(key, None)`을 쓰면 해당 사용자의 해당 기억만 삭제합니다. 이 함수의 `delete` 결과는 삭제된 레코드이며, key가 없으면 `None`입니다.

## "VS Code에서 uv 디버깅 설정과 프로그램 오류를 어떻게 구분하지?"

현재 `Check: memory` 구성은 `Debug with uv: memory` 작업을 시작하고, 작업이 debugpy 서버를 포트 `5678`에서 열면 같은 주소(`127.0.0.1:5678`)로 attach합니다. `tasks.json` 명령도 `uv run --frozen`을 사용합니다. 시작·준비 문자열을 명시해 백그라운드 작업 매처가 attach를 시작할 시점을 알 수 있게 합니다.

실행 결과를 다음처럼 구분합니다.

- 작업 터미널에 `DEBUGPY_STARTING_MEMORY` 뒤 `DEBUGPY_READY_MEMORY`가 나오지 않으면 `uv` 실행 또는 debugpy 서버 시작에서 막힌 것입니다.
- 준비 문구가 나온 뒤 attach 오류가 발생하면 연결 주소·포트 또는 이미 사용 중인 포트를 확인합니다.
- 디버거가 연결된 뒤 `main.py`에서 예외나 검사 실패가 발생하면 디버깅 설정과 별개로 프로그램 코드나 검사 결과를 확인합니다.

`DEBUGPY_READY_MEMORY`가 출력되고 task terminal이 계속 실행 중인 것은 정상입니다. 이 시점에 VS Code가 attach해야 하며, `debugpy.wait_for_client()`는 연결을 기다립니다. `Debug with uv: memory` 작업만 직접 실행하면 디버거가 연결되지 않아 계속 기다리므로, **실행 및 디버그**에서 `Check: memory`를 시작해야 합니다.

과거의 `WinError 2`는 존재하지 않는 `.venv\Scripts\python.exe`를 직접 실행하려던 구성에서 발생했습니다. 현재 구성은 해당 경로를 참조하지 않습니다.

## "`count(make_messages(candidate))`는 문자열 길이로 토큰을 세나?"

`candidate`는 선택 후보 대화 턴의 리스트입니다. `make_messages(candidate)`는 그 턴들을 포함한 전체 메시지 리스트를 만들고, `count(...)`는 전달받은 계수 함수에 그 리스트를 넘깁니다.

이 프로젝트에서는 `count`로 `support.count_tokens`를 전달합니다. 이 함수는 메시지 리스트를 compact JSON 문자열로 직렬화한 뒤, `tiktoken`의 `o200k_base` 인코딩으로 토큰 ID를 만들고 그 개수를 셉니다.

```python
messages = make_messages(candidate)
json_text = json.dumps(
    messages,
    ensure_ascii=False,
    separators=(",", ":"),
)
token_count = len(
    tiktoken.get_encoding("o200k_base").encode(json_text)
)
```

따라서 `len(str(messages))`처럼 Python 문자열의 글자 수를 세는 방식이 아닙니다. 역할 이름, JSON 구조, 메시지 본문을 포함해 직렬화한 입력 전체를 토큰화합니다. 이 값은 동일한 입력의 크기를 비교하고 예산을 적용하는 데 쓰며, API 서버의 실제 계량과 완전히 같다고 보장되지는 않습니다.

## "Bash 스크립트를 Windows CMD 형식으로 어떻게 바꾸지?"

Bash의 `.sh` 스크립트는 Windows 명령 프롬프트에서 직접 실행할 수 없으므로 `.cmd` 배치 파일로 바꿉니다. `#!/bin/bash` 줄은 제거하고, 스크립트 파일이 있는 폴더에서 명령이 실행되도록 다음 줄을 둘 수 있습니다.

```bat
@echo off
cd /d "%~dp0"
uv run --frozen python main.py check memory
exit /b %ERRORLEVEL%
```

`%~dp0`는 현재 배치 파일의 드라이브와 폴더 경로입니다. `cd /d`는 드라이브까지 함께 바꿉니다. 각 명령 직후 `if errorlevel 1`로 종료 코드를 확인해 `[PASS]` 또는 `[FAIL]`을 출력하고, 하나가 실패해도 나머지 명령을 계속 실행할 수 있습니다. 마지막에는 실패가 하나라도 있었는지에 따라 배치 파일의 종료 코드를 반환합니다.

이 프로젝트의 [`check.cmd`](./check.cmd)는 기존 `check.sh`의 명령 순서를 유지하며 각 단계를 표시합니다. 마지막의 `--live` 실행은 실제 API 요청과 비용이 발생할 수 있으므로 실행 전에 내용을 확인합니다.

로그 파일을 만들지 않고 `[PASS]`/`[FAIL]` 결과만 마지막에 보고 싶다면 [`check-summary.cmd`](./check-summary.cmd)를 사용합니다. 이 짧은 버전은 각 명령의 출력을 `>nul 2>&1`로 숨기고, 결과 문자열을 `RESULTS` 변수에 모은 뒤 한 번에 출력합니다. 실패 원인을 확인할 때는 출력을 보존하는 `check.cmd`를 사용합니다. `--live` 단계는 이 버전에서도 실제 API 호출과 비용이 발생할 수 있습니다.

## "프로젝트용 `.gitignore`에는 무엇을 넣지?"

`.gitignore`는 Git이 추적하지 않을 파일과 폴더를 지정합니다. Python 가상환경, 비밀 환경 파일, 생성 결과, 캐시는 제외하되, 예제 환경 파일과 잠금 파일, 디버깅 설정은 유지합니다.

```gitignore
.venv/
.env
.env.*
!.env.example
artifacts/
__pycache__/
*.py[cod]
```

`!.env.example`은 앞의 `.env.*` 규칙에서 예제 파일만 다시 포함합니다. 이미 Git이 추적 중인 파일은 `.gitignore`만 추가해도 추적이 해제되지 않습니다.

## 관련 파일

- [`main.py`](./main.py): 자료 선택 및 메시지 조립 함수
- [`support.py`](./support.py): `scenario.json` 읽기와 검사 실행 지원
- [`data/scenario.json`](./data/scenario.json): 현재 사용자와 예시 자료
- [`.vscode/launch.json`](./.vscode/launch.json): VS Code 디버거 attach 구성
- [`.vscode/tasks.json`](./.vscode/tasks.json): `uv run` 디버그 작업과 준비 마커
- [`.gitignore`](./.gitignore): 프로젝트 생성물 및 환경 파일 제외 규칙
- [`check.cmd`](./check.cmd): Windows CMD 실행 스크립트
- [`check-summary.cmd`](./check-summary.cmd): 마지막에 상태만 출력하는 간단한 실행 스크립트
