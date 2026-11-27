"""KANT NEXT DevDesk RAG. 이 파일의 빈칸만 작성하세요."""
from qdrant_client import models

import re
import support


def todo(message):
    raise NotImplementedError(message)


# 필수 1. 문서를 저장하고 현행 자료만 검색하기
def prepare_chunks(documents):
    chunks = []
    prepare_chunks.debug_docs= documents
    for document in documents:
        seen = set()
        number = 0
        for paragraph in document["paragraphs"]:
            # TODO: 문단 안의 연속 공백과 줄바꿈을 공백 하나로 정리합니다. 빈 문단, KANT NEXT | 내부 문서, 같은 문서 안의 중복 문단을 제외하는 조건은 제공됩니다.
            text_check= bool(re.search(r"\s{1,}", paragraph))
            text = " ".join(paragraph.split()) if bool(re.search(r"\s{1,}", paragraph)) else paragraph
            if not text or text == "KANT NEXT | 내부 문서" or text in seen:
                continue
            seen.add(text)

            #남은 문단 하나가 청크 하나입니다. document_id, title, category, status, source를 원문에서 복사하고 text에 정리한 본문을 넣습니다. 
            #chunk_id는 원문ID:번호입니다. 번호는 원문마다 0부터 시작하며 제외한 문단은 세지 않습니다.
            chunk = {
                "chunk_id": f"{document['document_id']}:{number}",
                "document_id": document["document_id"],
                "title": document["title"],
                "category": document["category"],
                "status": document["status"],
                "source": document["source"],
                "text": text

            }
            chunks.append(chunk)
            number += 1
            ## 이유: 문단을 유지하는 이유와 보존해야 할 메타데이터를 한두 줄로 적으세요. 
            #문단은 문서의 최소 단위로 chunking을 통해 검색과 답변의 근거가 됩니다. 어디서 추출했는지 document_id, title, category로 문단의 위치와 맥락을 파악하고, status로 현행을 구분하며, source로 문단의 조회 위치로 빠른 검색으로 개선하기 위함입니다. 
    
    return chunks


def build_index(chunks, embedder):
    texts = ["passage: " + row["title"] + "\n" + row["text"] for row in chunks]
    
    
    vectors = embedder.encode(texts, normalize_embeddings=True)

    client = support.empty_store(len(vectors[0]))
    points = []
    for i, (row, vector) in enumerate(zip(chunks, vectors, strict=True)):
        #todo("i, vector, row를 Qdrant PointStruct에 연결하세요.")
        point = models.PointStruct(id=i, vector=vector, payload=row)
        points.append(point)
    client.upsert(collection_name="devdesk", points=points, wait=True)
    return client


def search(client, embedder, question, category, top_k=2):
    if type(top_k) is not int or not 1 <= top_k <= 5:
        raise ValueError("top_k는 1~5의 정수여야 합니다.")
    vector = embedder.encode(["query: " + question], normalize_embeddings=True)[0]
    # Filter는 조건을 담는 모델 클래스이며, 생성자 인자로 조건 필드를 설정합니다.
    # must: 모든 조건을 만족(AND), must_not: 어떤 조건도 만족하지 않음(NOT).
    # should: 선택 조건 중 하나 이상 만족(OR), min_should: 지정한 개수 이상 만족.
    # 여기서는 status와 category가 모두 일치해야 하므로 must를 사용합니다.
    scope = models.Filter(must=[
        models.FieldCondition(
            key="status",
            match=models.MatchValue(value="current")
        ),
        models.FieldCondition(
            key="category",
            match=models.MatchValue(value=category)
        )
    ])

    
    hits = client.query_points(collection_name="devdesk", query=list(vector),
                               query_filter=scope, limit=top_k, with_payload=True).points

    
    return [{**hit.payload, "score": hit.score} for hit in hits]


# 필수 2. 별칭 검색을 개선하고 답변을 비교하기
def rewrite_query(question, aliases):
    rewritten = question
    for alias, formal_name in aliases.items():
        # todo("현재 문자열에서 alias를 formal_name으로 바꾸세요.")
        print(f"[관측] rewrite_query 입력: {rewritten!r} ({type(rewritten).__name__})")
        print(
            f"[관측] 별칭 치환: {alias!r} ({type(alias).__name__}) -> "
            f"{formal_name!r} ({type(formal_name).__name__})"
        )
        # 기존의 qeustion str 값을 formal_name으로 바꾸는 작업을 진행 
        rewritten = rewritten.replace(alias, formal_name)
    return rewritten


def answer_question(question, rows, generate):
    if not rows:
        return {"answer": "확인할 문서가 없습니다.", "citations": [], "needs_human": True}
    # todo("각 검색 결과를 [chunk_id] 본문으로 묶고 빈 줄로 연결하세요.")
    context = "\n\n".join(
            f"[{row['chunk_id']}] {row['text']}" for row in rows
    )   

    print("[관측] answer_question: generate 호출")
    reply = support.validate_shape(generate(question, context))
    print(f"[관측] citations: {reply['citations']}")
    allowed = {row["chunk_id"] for row in rows}
    print(f"[관측] 허용된 chunk_id: {allowed}")

    # todo("검색 결과에 없는 출처가 하나라도 있는지 검사하세요.")
    if not set(reply["citations"]).issubset(allowed):
        raise ValueError("검색하지 않은 출처가 있습니다.")
    if reply["needs_human"] == bool(reply["citations"]):
        raise ValueError("답변에는 출처가 필요하며 담당자 확인에는 출처를 비웁니다.")
    return reply


def make_golden():
    # todo("답이 있는 사례와 자료가 없는 사례를 하나씩 작성하세요.")
    # documents = support.load_documents()
    # print("디버깅 documents", documents)

    return [
        {
         "question_id": "question_01",
         "question":"초록문 원격 접속 승인은 어디에 요청하나요?",
         "category": "access", 
         "reference_answer": "VPN 원격 접속을 사용하려면 보안팀에 승인을 요청해야 합니다" , 
         "relevant_document_ids": ["vpn"],
         "required_terms": ["보안팀"],

        },
         {
        "question_id": "question_02"  ,
        "question": "해외 지사의 휴가 승인은 절차느 어디서 확인하나요?" , 
        "category": "overseas" , 
        "reference_answer": "해당 내용은 제공된 자료에서 확인할수 없습니다.", 
        "relevant_document_ids": [],
        "required_terms": [],
        
                },
    ]


def measure(case, rows, reply):
    expected = set(case["relevant_document_ids"])
    found = {row["document_id"] for row in rows}
    # todo("필요한 문서 중 찾은 비율을 계산하세요. 필요한 문서가 없으면 None입니다.")
  
    print("expected", expected, len(expected))
    print("found", found, len(found))
    recall = len(found)/len(expected) if expected  else None
    answer_ok = (all(term in reply["answer"] for term in case["required_terms"])
                 and not reply["needs_human"]) if expected else reply["needs_human"]
    failure = "없음"
    if expected and recall < 1:
        failure = "검색 누락"
    elif not answer_ok:
        failure = "답변 확인 필요" if expected else "보류 실패"
    # 관측: 실제 evaluate 결과에서 개선, 악화 질문과 답변 본문을 확인해 기록합니다.
    print(f"[관측] 질문: {case.get('question', '(검사 사례)')}")
    print(f"[관측] 답변: {reply['answer']}")
    print(
        f"[관측] recall={recall}, "
        f"answer_check={bool(answer_ok)}, failure={failure}"
    )
    return {"document_recall": recall, "answer_check": bool(answer_ok), "failure": failure}


# 선택 심화 1. 두 검색 순위를 합쳐 근거를 모으기
def fuse_rankings(rankings, top_k=2):
    # 선택 심화: 문제의 RRF 규칙에 맞춰 직접 작성하세요.
    return todo("검색 순위 목록을 RRF 점수로 합치세요.")


if __name__ == "__main__":
    support.cli(globals())
