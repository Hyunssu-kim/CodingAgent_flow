# Design-Aware AI Coding Platform (MVP)

**한 줄 요약**: 설계 문서를 지속적으로 상기하는 AI 코딩 에이전트와 MCP 기반 품질 리포트를 결합한 프로덕션 지향 플랫폼.

![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688)
![Ruff](https://img.shields.io/badge/ruff-lint-ef476f)
![Pytest](https://img.shields.io/badge/pytest-test-0a9edc)
![Coverage](https://img.shields.io/badge/coverage-coverage-06d6a0)

> 스크린샷/데모 GIF를 여기에 추가하세요.
>
> - `docs/demo.png` 또는 `docs/demo.gif`

![Demo](docs/demo.png)

---

## 프로젝트 소개
AI가 단순히 코드를 생성하는 것이 아니라, **설계 문서(ARCHITECTURE/CODING_RULES/API_CONTRACT)를 매 요청마다 검색·요약**해 컨텍스트로 주입합니다. 결과물에 대해 **MCP Tool Server가 lint/test/coverage를 실행**하여 하나의 품질 리포트로 제공합니다.

**주요 기능**
- Prompt/Context Engineering: 역할/제약/출력 스키마 기반 템플릿
- Design Memory Snapshot: 설계 문서 맥락을 지속 저장
- RAG 검색: Top-k 문단 검색 및 컨텍스트 주입
- MCP Tool Server: lint/test/coverage 격리 실행
- 통합 품질 리포트 UI

---

## 핵심 컨셉
### Design-Aware AI Coding이란?
프로젝트 설계 문서와 코딩 규칙을 매 요청마다 검색하고 Memory Snapshot으로 요약해 **일관성 있는 코드 품질과 설계 준수**를 보장하는 접근입니다.

### 기존 AI 코딩 도구와의 차이점
- **Context 지속성**: 설계 문서가 항상 상기됨
- **품질 자동화**: MCP 서버에서 lint/test/coverage 분리 실행
- **운영 관점**: Prompt/Memory 관리 + 리포트 통합

### 아키텍처 다이어그램
```
+-------------------+       +------------------------+
|       UI          |       |   MCP Tool Server      |
| (Run Console)     |       |  /tool/lint|test|cov   |
+---------+---------+       +------------+-----------+
          |                              ^
          v                              |
+-------------------+    HTTP JSON       |
| FastAPI Orchestr. |--------------------+
| - Prompt Registry |
| - RAG Retriever   |
| - Memory Manager  |
| - LLM Gateway     |
| - MCP Client      |
+---------+---------+
          |
          v
+-------------------+
| Design Docs (RAG) |
| ARCH/CODING/API   |
+-------------------+
```

---

## 주요 기능
1) **Prompt/Context Engineering**
- role/constraints/output schema 기반 프롬프트 템플릿

2) **Design Memory System**
- 설계 문서 기반 Memory Snapshot 갱신 및 누적

3) **RAG 기반 문서 검색**
- 설계 문서 벡터화 후 Top-k 문단 검색

4) **MCP Tool Server**
- lint/test/coverage 실행을 별도 서버로 격리

5) **통합 품질 리포트**
- 단일 요청에 LLM 결과 + 품질 리포트 제공

---

## 설치 및 실행
### Prerequisites
- Python 3.11+
- pip

### 1) 설치
```
pip install -r requirements.txt
```

### 2) 환경 변수 설정
`.env.example`을 참고해 `.env`를 생성하세요.
```
cp .env.example .env
```

핵심 값:
- `APP_ENV=dev|prod`
- `MCP_SERVER_URL=http://localhost:8090`

### 3) 개발 모드 실행
**Orchestrator**
```
uvicorn apps.orchestrator.main:app --reload --port 8080
```

**MCP Tool Server**
```
uvicorn services.mcp_server.server:app --reload --port 8090
```

### 4) 프로덕션 모드 (예시)
- Orchestrator와 MCP Server를 독립 서비스로 배포
- MCP 서버는 도구 실행 격리를 위해 별도 컨테이너/VM 권장

---

## API 문서 (요약)
### POST /run
**Request**
```
{
  "task_type": "code_generation",
  "user_input": "Implement a safe file reader",
  "project_id": "default",
  "options": {}
}
```

**Response (sample)**
```
{
  "llm_output": "...",
  "memory_snapshot": "Memory Snapshot: ...",
  "retrieved_context": ["..."],
  "quality_report": {
    "lint": {"status": "ok", "detail": {"count": 0, "violations": []}},
    "test": {"status": "passed", "detail": {"summary": {"passed": 1}}},
    "coverage": {"status": "ok", "detail": {"coverage_percent": 95.0, "missing_lines": []}}
  }
}
```

### cURL 예시
```
curl -X POST http://localhost:8080/run \
  -H "Content-Type: application/json" \
  -d '{"task_type":"code_generation","user_input":"Create a hello function","project_id":"demo"}'
```

### MCP Tool Server
- `POST /tool/lint`
- `POST /tool/test`
- `POST /tool/coverage`

---

## 프로젝트 구조
```
apps/
  orchestrator/   # FastAPI 오케스트레이터
  ui/             # 프론트 UI
services/
  mcp_server/     # MCP Tool Server
scripts/          # 문서 ingest 및 seed
examples/         # 데모 시나리오
docs/             # 설계 문서
```

---

## 기술적 의사결정
- **왜 FastAPI?**
  - 간결한 선언형 API, Python 생태계 친화적, 확장 쉬움
- **왜 MCP 서버 분리?**
  - 코드 품질 도구 실행을 API로부터 분리해 격리/확장 가능
- **왜 Memory Snapshot?**
  - 설계 맥락을 누적 요약해 일관성 있는 코드 생성 지원

---

## 향후 계획
- VS Code Extension 연동
- 실제 LLM Gateway 연결
- 보안/정적 분석 도구 추가 (bandit, mypy 등)

---

## 라이센스 및 기여
- License: MIT (변경 가능)
- PR 및 이슈 환영
