# 🛠️ MCP Tool 리팩토링 계획서

이 문서는 `src/server_mcp.py`에 정의된 AI 에이전트 도구(Tool)들을 `tool-design` 가이드라인에 맞추어 개선하는 상세 계획입니다.

## 🎯 주요 목표
1. **명확한 Docstring 작성**: 각 함수가 **무엇을 하는지(What)**, **언제 사용해야 하는지(When to use)**, **무엇을 반환하는지(Returns)**, **어떤 오류가 발생할 수 있는지(Errors)**를 한국어로 명확히 기술.
2. **에러 핸들링 고도화**: 단순한 텍스트 에러 문구가 아닌, AI가 실패 사유를 인지하고 **복구 방법(Suggestion)**을 스스로 시도할 수 있도록 모든 에러를 구조화된 JSON 형태로 반환.
3. **입력 타입 명확화**: `check_portfolio_risk` 함수가 번거로운 문자열 파싱 대신, Python 내장 타입인 `List[Dict[str, Any]]`를 직접 인자로 받도록 우선적으로 설계.

## 📝 작업 내용 요약
- 대상 파일: `src/server_mcp.py`
- 수정 범위: 8개 `@mcp.tool` 함수 블록
- 변경 사항 상세:
  - 각 함수 상단의 문서화 문자열(Docstring) 전면 재구성 (한국어 적용)
  - 예외 처리(`except Exception as e`) 영역에서 반환 형식을 `{"error": "...", "suggestion": "..."}` 의 JSON 구조로 수정
  - `check_portfolio_risk` 함수의 `holdings` 파라미터 타입을 명시적으로 수정하고 불필요한 직렬화/역직렬화(`json.loads()`) 과정을 삭제
  - AI 에이전트가 반환 데이터를 완벽하게 파싱할 수 있도록 모든 `json.dumps()`에 `ensure_ascii=False` (한글 깨짐 방지)를 일괄 적용

이 계획에 따라 기존 함수의 핵심 비즈니스 로직은 안전하게 보존하면서, 오직 AI가 Tool을 더 잘 활용할 수 있도록 개선합니다.
