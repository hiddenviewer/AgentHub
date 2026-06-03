# 💡 Architecture Decision Records (ADR)

이 디렉토리는 AgentHub 프로젝트의 주요 아키텍처 및 기술적 결정 사항들을 기록하는 공간입니다. 
결정에 대한 맥락(Context), 고려한 대안, 최종 결정 및 그 결과(Consequences)를 문서화하여 지식을 누적합니다.

## 📝 ADR 작성 규칙
* 파일명 형식: `adr-[번호]-[주제-영문-소문자].md` (예: `adr-001-google-news-url-decoding.md`)
* 포함해야 할 필수 섹션:
  1. **상태 (Status):** 제안(Proposed), 승인(Accepted), 거절(Rejected), 대체됨(Deprecated)
  2. **맥락 (Context):** 결정을 내리게 된 배경과 문제 상황
  3. **고려한 대안들 (Alternatives Considered):** 장단점 비교
  4. **결정 (Decision):** 최종 채택한 솔루션과 그 근거
  5. **결과 (Consequences):** 이 결정으로 인한 트레이드오프나 향후 영향

---

## 🗂️ 결정 기록 목록

| 번호 | 결정 사항 | 상태 | 작성일 |
| :--- | :--- | :---: | :---: |
| 001 | [Google News URL 디코딩 및 번역 프레임워크 설계](adr-001-google-news-url-decoding.md) | Accepted | 2026-06-04 |
