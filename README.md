# 설계 인지형 AI 코딩 플랫폼 (MVP)

설계 문서를 컨텍스트(RAG)로 유지하고, MCP Tool Server로 품질 도구를 실행하며, 프롬프트/메모리/실행 기록을 운영 UI에서 확인할 수 있는 경량 AI 코딩 플랫폼입니다.

## 현재 동작하는 기능
- FastAPI 오케스트레이터(`/run`, `/runs`, `/prompts`, `/memory` API)
- 로컬 설계 문서 RAG (`docs/ARCHITECTURE.md`, `docs/CODING_RULES.md`, `docs/API_CONTRACT.md`)
- 메모리 스냅샷 JSON 저장 (`data/memory/*.json`)
- MCP Tool Server 기반 lint/test/coverage (ruff/pytest/coverage)
- 실행 기록 JSON 저장 (`data/run_store.json`) + 통계 엔드포인트
- 작업 실행 및 운영 지표를 보여주는 최소 UI

## 아키텍처
```
+-------------------+       +------------------------+
|       UI          |       |   MCP Tool Server      |
| (Run + Ops UI)    |       |  /tool/lint|test|cov   |
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
| - Run Store       |
+---------+---------+
          |
          v
+-------------------+
| Design Docs (RAG) |
| ARCH/CODING/API   |
+-------------------+
```

## 빠른 시작
### 1) 가상환경 생성
```
python -m venv .venv
```

### 2) 의존성 설치
```
.\.venv\Scripts\python -m pip install -r requirements.txt
```

### 3) 환경 변수 설정
```
copy .env.example .env
```

### 4) 서비스 실행 (터미널 2개)
오케스트레이터
```
.\.venv\Scripts\python -m uvicorn apps.orchestrator.main:app --reload --port 8080
```

MCP Tool Server
```
.\.venv\Scripts\python -m uvicorn services.mcp_server.server:app --reload --port 8090
```

### 5) UI 접속
`http://localhost:8080/ui`

## 설정 메모
- 기본 `.env`는 `LLM_PROVIDER=stub`이며 프롬프트를 그대로 에코합니다(오프라인 데모용).
- Gemini 호출 시 `LLM_PROVIDER=gemini`와 `LLM_API_KEY=...`가 필요합니다.
- MCP 도구는 `ruff`, `pytest`, `coverage`가 필요합니다(이미 `requirements.txt`에 포함).

## API
### POST /run
```
{
  "task_type": "code_generation",
  "user_input": "Implement a safe file reader",
  "project_id": "default",
  "options": {}
}
```

Response (sample)
```
{
  "llm_output": "...",
  "memory_snapshot": "Memory Snapshot: ...",
  "retrieved_context": ["..."],
  "quality_report": {
    "lint": {"status": "ok", "detail": {"count": 0, "violations": []}},
    "test": {"status": "passed", "detail": {"summary": {"passed": 1}}},
    "coverage": {"status": "ok", "detail": {"coverage_percent": 95.0, "missing_lines": []}}
  },
  "run_id": "...",
  "duration_ms": 123
}
```

### GET /runs
최근 실행 목록. `project_id`, `limit` 옵션 사용 가능.

### GET /runs/{run_id}
단일 실행 기록 조회.

### DELETE /runs/{run_id}
단일 실행 기록 삭제.

### GET /runs/stats
실행 통계(작업 유형별 카운트, 최근 실행 시간).

### GET /prompts
프롬프트 템플릿 목록.

### POST /prompts
프롬프트 템플릿 생성.

### GET /memory
프로젝트 메모리 스냅샷 조회.

### POST /memory/refresh
Placeholder. 스냅샷은 갱신하지만 문서 재-인덱싱은 아직 미구현.

### GET /memory/{project_id}/history
메모리 히스토리 조회.

### DELETE /memory/{project_id}
프로젝트 메모리 삭제.

### GET /memory/stats
메모리 통계.

## UI
- 실행 콘솔: 작업 요청, LLM 출력, 검색 컨텍스트, 메모리 스냅샷, 품질 리포트 확인
- 운영 대시보드: 실행 히스토리, 프롬프트 레지스트리, 메모리 통계

## 데모 자료
- 데모 가이드: `docs/DEMO.md`
- 예제 요청: `examples/demo_requests.json`
- PowerShell 데모 러너: `scripts/demo_requests.ps1`

## 구현 메모 (현재 동작 기준)
- RAG는 해시 기반 임베딩(placeholder)을 사용하며 `data/vectordb/vector_db.json`에 저장됩니다.
- 설계 문서는 앱 시작 시 인덱싱되며 `/memory/refresh`는 아직 재-인덱싱하지 않습니다.
- 에이전트는 첫 번째 코드 블록을 코드로, 두 번째 블록을 테스트 케이스로 사용합니다.
- MCP 도구는 JSON 테스트 케이스를 pytest 코드로 변환합니다(`services/mcp_server/tools/testgen.py`).
- 프롬프트 레지스트리는 메모리 기반이며 재시작 시 초기화됩니다.

## 프로젝트 구조
```
apps/
  orchestrator/   # FastAPI 오케스트레이터
  ui/             # 관리 UI
services/
  mcp_server/     # MCP Tool Server
scripts/          # 데모 헬퍼
examples/         # 샘플 시나리오
docs/             # 설계 문서
```

## 로드맵
- 벡터 스토어 통합 (FAISS/Chroma)
- 인증 + 멀티 테넌시 프로젝트 분리
- MCP 도구 샌드박싱
- IDE 확장 (VS Code / IntelliJ)
