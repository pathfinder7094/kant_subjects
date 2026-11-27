# 학습 Wiki

## Qdrant `Filter`와 SQL `WHERE`의 비교

### 질문
`qdrant_client` SDK의 `Filter`로 `scope`를 정의하여 Qdrant에 주입되는 벡터의 데이터 조건절을 찾는 함수이며, 관계형 데이터베이스의 `WHERE`절과 유사한가?

### 답변
부분적으로 유사하지만, 정확한 표현은 다음과 같다.

`models.Filter(must=[...])`는 벡터 자체가 아니라 저장된 점(point)의 payload 메타데이터를 필터링한다.

- `must`는 모든 조건을 만족해야 한다는 의미이므로 SQL의 `AND`와 같다.
- `must_not`은 어떤 조건도 만족하지 않아야 한다.
- `should`는 하나 이상의 선택 조건을 만족한다.
- `min_should`는 `should` 조건 중 만족해야 하는 최소 개수를 지정한다.

이 프로젝트의 [main.py](main.py:70)에서는 다음 두 payload 조건을 동시에 적용한다.

```python
scope = models.Filter(must=[
    models.FieldCondition(
        key="status",
        match=models.MatchValue(value="현행")
    ),
    models.FieldCondition(
        key="category",
        match=models.MatchValue(value=category)
    )
])
```

- `status`가 `"현행"`이어야 한다.
- `category`가 검색에 전달한 `category`와 같아야 한다.

[main.py](main.py:83)에서 `query_filter=scope`를 전달하면 질의 벡터로 유사도 검색하기 전에 또는 검색 과정과 함께 이 후보 조건을 적용하여 필터를 만족하는 점만 검색 결과로 고려한다.

### 잘못된 개념 지적
“주입되는 벡터의 데이터 조건절을 찾는 함수”라는 표현은 정확하지 않다. `Filter`는 벡터의 값이나 벡터 차원을 직접 비교하는 것이 아니라, payload의 필드를 검사한다.

더 정확한 문장은 다음과 같다.

> `Filter`로 검색 대상 점들의 payload 조건을 제한한 뒤, 질의 벡터와 저장된 벡터 간 유사도를 계산하여 관련 문서를 검색한다.

SQL의 `WHERE`와는 후보 집합을 제한한다는 점에서 유사하다. 차이점은 SQL이 관계형 테이블의 행을 필터링하고, Qdrant는 벡터 유사도 검색과 payload 메타데이터 필터링을 결합한다는 점이다.

## Python 딕셔너리에서 `{**hit.payload, "score": hit.score}`의 의미

### 질문
`hit.payload` 앞의 `**`는 왜 사용하며, 반환 코드 `{**hit.payload, "score": hit.score}`는 무엇을 의미하는가?

### 답변
`**`는 딕셔너리를 펼치는(dictionary unpacking) 문법이다. 이때 피연산자 `hit.payload`의 각 키와 값을 새 딕셔너리에 복사한다.

예를 들어 `hit.payload`가 다음이라면:

```python
{
    "chunk_id": "doc-1:0",
    "document_id": "doc-1",
    "text": "본문"
}
```

다음 코드는:

```python
{**hit.payload, "score": hit.score}
```

실질적으로 유사한 새 딕셔너리를 만든다.

```python
{
    "chunk_id": "doc-1:0",
    "document_id": "doc-1",
    "text": "본문",
    "score": 0.95
}
```

반환 형태가 `[{...}, {...}]`인 이유는 리스트 컴프리헨션을 사용하기 때문이다.

```python
return [{**hit.payload, "score": hit.score} for hit in hits]
```

이 코드는 `hits`의 각 검색 결과 `hit`에 대해 새 딕셔너리를 만들고, 그 딕셔너리를 모아 하나의 리스트로 반환한다.

### 잘못된 개념 지적
`**`는 포인터 역참조나 주소 해제 연산자가 아니다. Python의 딕셔너리 리터럴에서 키-값 쌍을 펼치는 문법이다.

주의할 점은 `hit.payload`가 딕셔너리 또는 매핑 형식이어야 한다는 것이다. 여기서 `hit.payload`는 Qdrant 검색 결과에 포함된 저장된 payload를 의미하며, `"score"`는 유사도 점수를 별도 키로 추가한다.

같은 키가 payload와 뒤의 명시적 항목에 모두 있으면 뒤의 값이 덮어쓴다. 예를 들어 payload에 이미 `"score"`가 있다면, 이 코드의 `hit.score`가 payload의 기존 `"score"`를 덮어쓴다.

## 문자열 리스트를 하나의 문자열로 합치기

### 질문
Python에서 문자열(`str`) 값들로 이루어진 리스트를 하나의 문자열로 합치는 방법은?

### 답변
문자열 리스트라면 `str.join()`을 사용한다. `join()` 앞의 문자열이 각 요소 사이에 들어갈 구분자다.

```python
words = ["안녕", "하세요"]

" ".join(words)       # "안녕 하세요"
"".join(words)        # "안녕하세요"
"\n".join(words)      # 줄바꿈으로 연결
"\n\n".join(words)    # 빈 줄을 두고 연결
```

현재 `answer_question`처럼 각 검색 결과를 `[chunk_id] 본문` 모양으로 만들고, 항목 사이를 빈 줄로 구분하려면 생성식과 `join()`을 함께 사용할 수 있다.

```python
context = "\n\n".join(
    f"[{row['chunk_id']}] {row['text']}"
    for row in rows
)
```

여기서 각 반복 결과는 문자열이고, `"\n\n"`가 항목 사이에 들어간다. `rows`가 비어 있으면 결과는 빈 문자열이다.

### 잘못된 개념 지적
`for` 반복문을 문자열 뒤에 붙여 쓰는 것만으로는 여러 문자열을 연결할 수 없다. 반복 결과를 하나로 모으려면 `join()` 같은 결합 연산이 필요하다.

또한 `join()`은 문자열 시퀀스를 기대하므로 리스트에 정수 등 문자열이 아닌 값이 섞여 있으면 `TypeError`가 발생한다. 그런 값도 문자열로 표현하려는 경우에만 `str(value)` 또는 `map(str, values)`를 명시적으로 적용한다.
