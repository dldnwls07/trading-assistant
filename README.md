# Trading Assistant

[![CI](https://github.com/dldnwls07/trading-assistant/actions/workflows/ci.yml/badge.svg)](https://github.com/dldnwls07/trading-assistant/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Issues](https://img.shields.io/github/issues/dldnwls07/trading-assistant)](https://github.com/dldnwls07/trading-assistant/issues)

간단한 주식투자 보조 도구(미국 주식 우선). 현재 목표: CLI 프로토타입으로 기능 검증 후 확장(웹 앱, Chrome 확장) 및 모네타이즈.

## 개발 환경 (빠른 시작)

**참고**: 개발 규칙이 업데이트되었습니다 — `DEVELOPMENT_GUIDELINES.md`를 확인하세요.


1. Python 3.10+ 권장
2. 가상환경 생성 및 활성화
   - `python -m venv .venv`
   - Windows: `.\.venv\Scripts\activate`, macOS/Linux: `source .venv/bin/activate`

3. 개발 도구 설치 (선택)
   - `pip install pre-commit detect-secrets black isort flake8`

4. pre-commit 설치 및 초기화
   - `pre-commit install`
   - (선택) `pre-commit run --all-files`

5. 시크릿 baseline 생성(로컬에서 한 번만 실행)
   - `pip install detect-secrets`
   - `detect-secrets scan > .secrets.baseline`
   - 리뷰 후 커밋: `.secrets.baseline`은 커밋하지만 실제 비밀은 절대 포함하지 마세요.


## 안전 지침
- `.env` 파일을 사용해 민감 정보를 보관하고 `.env`는 절대 커밋하지 마세요. `.env.example`를 템플릿으로 사용하세요.
- GitHub 리포지토리에 민감 정보가 올라가면 즉시 회수하세요 (키 교체, 히스토리 제거).


## 추가 문서
- `PROJECT_PLAN.md` — 프로젝트 계획 및 체크리스트
- `SECURITY.md` — 시크릿/보안 지침
- `DEVELOPMENT_GUIDELINES.md` — 개발 원칙 및 작업 규칙 (변경 전 승인, 하드코딩 금지, AI 프롬프트 관리 등)

> 개발 규칙을 준수하지 않은 변경은 반려될 수 있습니다. PR 생성 시 반드시 `PULL_REQUEST_TEMPLATE.md` 체크리스트를 채워주세요.
