"""main.py의 todo(...) 부분을 작성하세요. support.py와 checks.py는 그대로 사용합니다."""
import copy
import hashlib
import json
import sys

import support


def todo(message):
    raise NotImplementedError(message)


# 필수 1. 필요한 자료와 사용자 기억 관리하기
def select_context(items, user_id, now):
    kept = []
    for item in items:
        # todo("접근 범위, 신뢰, 현행 여부와 만료 조건")
       
        allowed = bool(item["user_id"] == "public" or item["user_id"] == user_id ) and bool(item["trusted"] and item["active"]) and bool(item["expires_at"] is None or item["expires_at"] > now )
        if allowed:
            kept.append(copy.deepcopy(item))
    # 이유: 높은 우선순위의 자료를 먼저 고르면 어떤 문제가 생기는지 적으세요.
    return sorted(kept, key=lambda item: (-item["priority"], item["id"]))


def memory_action(records, user_id, action, name, value=None):
    support.validate_memory_input(user_id, action, name, value)
    key = f"{user_id}:{name}"
    if action == "read":
        # todo("현재 사용자의 기억 조회")
        record = records.get(key)
        return copy.deepcopy(record) if record is not None else None  
    if action == "create":
        if key in records:
            raise ValueError("이미 있는 기억입니다. update를 사용하세요.")
        # todo("새 기억 저장")
        records[key] = copy.deepcopy(value)
    elif action == "update":
        if key not in records:
            raise KeyError("수정할 기억이 없습니다.")
        records[key] = copy.deepcopy(value)
    elif action == "delete":
        return records.pop(key, None)
    return copy.deepcopy(records[key])


def build_messages(prefix, question, context, turns, summary):
    data = json.dumps({"reference_data": context, "summary": summary}, ensure_ascii=False)
    history = [message for turn in turns for message in turn["messages"]]
    # 이유: 장기 기억과 세션 상태의 차이, 자료와 지시를 나누는 이유를 적으세요.
    # 세션 상태가 유지되는 경우도 있지만 세션 만료 혹은 이전 대화기록에서 저장된 메모리로 부터 유사한 답변 조건을 찾아 답변이 필요할때가 있다. 이를 최신화하거나 과거의 이력에서 답변에 필요한 조건을 찾아 답변의 표현을 풍부하게 만들기 위해 장기기억에 유저의 특정 질의한 데이터를 저장하고 관리한다. 
    # 자료와 지식의 메세지를 구분하여 사용자의 질의 의도를 파악하여 제공되는 자료범위에 대해 발화 경계를 구분한 대화의 맥락에 맞는 정확한 답변을 출력하기 위함. 
    # print(data, history)
    # todo("고정 지시, 참고 자료, 대화, 현재 질문 순서의 메시지")
    return [
         { "role" : "developer", "content" : prefix },
         { "role" : "user", "content" : data },
          *history ,
         { "role" : "user", "content" : question }
    ]


# 필수 2. 긴 대화를 줄이고 반복 입력 재사용하기
def summarize(turns):
    # print(turns)
    summary = {}
    for turn in turns:
        for name, value in support.fact_lines(turn["messages"][0]["content"]):
            # todo("최신 값과 출처 턴")
            summary[name] = {
                "value" : value,
                "source_turn_id" : turn["id"] 
            }
    return summary


def select_window(turns, limit, reserve, margin, make_messages, count):
    support.validate_budget(limit, reserve, margin)
    # todo("입력에 쓸 수 있는 예산")
    # print(turns, limit, reserve, margin,  make_messages, count)
    budget = limit - reserve - margin
    if budget <= 0 or count(make_messages([])) > budget:
        raise ValueError("고정 입력만으로 예산을 넘었습니다.")
    kept = []
    for turn in reversed(turns):
        candidate = [turn, *kept]
        # todo("전체 후보 입력이 예산을 넘는지")
        if budget < count(make_messages(candidate)):
        
            break
        kept = candidate
    # 관측: 압축 비교 후 토큰 수, 빠진 사실, 선택한 한도를 기록합니다.
    return kept


def cache_key(prefix, user_id):
    # todo("사용자와 고정 지시로 만드는 캐시 키")
    cache_text= user_id+"\n"+prefix
    encodded_text= cache_text.encode("utf-8")
    return hashlib.sha256(encodded_text).hexdigest()
    # 관측: 실제 캐시 읽기/쓰기와 비용을 확인하고 미관측이면 그대로 적습니다.


# 선택 심화 1. 새 대화만 반영하고 변경 이력 남기기
def merge_summary(previous, turns):
    return todo("선택 심화: 새 턴의 요약과 변경 이력")


if __name__ == "__main__":
    raise SystemExit(support.cli(sys.modules[__name__]))
