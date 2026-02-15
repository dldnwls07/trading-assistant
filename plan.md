# 🗑️ 프로젝트 정리 계획 (확정)

사용자 확인(`배포는 사용함`)에 따라 배포 관련 파일은 유지하고, 나머지 불필요한 파일 및 디렉토리만 삭제합니다.

## 1. 삭제 대상 (확정)

### 📦 임시 스크립트
*   `run_backtest_demo.py`: 백테스트 데모
*   `test_market.py`: 시장 데이터 테스트
*   `extract_strings.py`: 문자열 추출 유틸
*   `read_pdf.py`: PDF 읽기 유틸

### 📄 문서 및 참고 자료
*   `refactoring_plan.md`: 완료된 계획서
*   `claude_skills_ebook_v3.pdf`: 대용량 참고 문서

### 📂 빈 디렉토리 (루트)
*   `charts/`
*   `data/` (주의: `src/data`는 유지)

## 2. 유지 대상 (배포용)
*   `Procfile`
*   `render.yaml`
*   `runtime.txt`
*   `start_render.sh`

## 3. 실행
위 삭제 대상을 Powershell 명령어로 제거합니다.
