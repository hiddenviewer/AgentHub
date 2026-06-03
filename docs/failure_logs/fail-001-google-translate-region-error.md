# FAIL-001: 구글 뉴스 리다이렉트 주소의 구글 번역 리전 에러 사건

* **상태 (Status):** Resolved
* **작성자 (Author):** Antigravity (AI Coding Assistant)
* **작성일 (Date):** 2026-06-04

---

## 1. 사건/현상 (Incident/Symptom)
사용자가 AI 에이전트 영어 뉴스의 번역 기능(🌐 한글 번역 보기)을 클릭했을 때, 다음과 같은 에러 메시지가 표시되면서 원래 본문 번역이 완전히 거부되는 현상이 있었습니다.

> **에러 메시지:** `This translation service isn't available in your region`
> **호출 주소:** `https://news-google-com.translate.goog/rss/articles/...`

## 2. 원인 분석 (Root Cause Analysis)
* Google News RSS가 제공하는 링크는 원본 뉴스 사이트의 실제 링크가 아니라 구글 뉴스가 내부적으로 래핑(Wrapping)한 리다이렉트용 중간 링크(`news.google.com/rss/articles/...`)입니다.
* 구글 번역 프록시(`*.translate.goog`)는 대상 페이지를 자체적인 프록시 환경으로 가져와 실시간으로 번역하는데, 구글 뉴스의 내부 리다이렉션이 얽힌 동적 주소를 입력받으면 세션 보안 정책 및 국가 차단(Geo-blocking) 시스템과 충돌을 일으킵니다.
* 결과적으로 사용자의 지역(Region)에서 번역이 불가능하다는 보안 샌드박스 페이지를 반환하게 되었습니다.

## 3. 해결 및 시도한 방법 (Mitigation & Troubleshooting)
1. **번역 프록시 포맷 변경 시도 (실패):**
   * 프록시 방식(`*.translate.goog`) 대신 표준 번역 페이지 주소(`translate.google.com/translate?u=`)로 파라미터를 변경해 넘겨보았으나, 구글 뉴스 주소 자체가 걸려 있는 한 번역을 시도하는 시점에 동일한 리디렉션 거부 에러가 났습니다.
2. **크롤링 시점의 실제 URL 디코딩 도입 (성공):**
   * 문제의 원인이 '구글 뉴스 도메인의 중간 주소'이기 때문에, 이를 해결하려면 최종 본문 기사가 실린 원본 사이트 도메인(예: `techcrunch.com`)의 다이렉트 URL을 구해야 함을 깨달았습니다.
   * `googlenewsdecoder` 라이브러리를 연동해 크롤링 단계에서 base64 및 `batchexecute` 프로토콜을 통과하여 디코딩된 최종 진짜 도메인 주소를 얻도록 [collect_news.py](file:///Users/user/Projects/ai/AgentHub/scripts/collect_news.py)를 개편했습니다.
   * 복호화된 최종 URL을 구글 번역기에 던지자, 리전 제약 없이 매우 깔끔하게 번역 기능이 동작했습니다.

## 4. 교훈 및 방지 대책 (Lessons Learned & Action Items)
* **사전 도메인 검증의 중요성:** 타사 서비스(구글 번역기 등)와 간접 연동할 때는 입력 URL이 중간 리다이렉션을 거치지 않는 순수한 정적 도메인인지 사전에 꼼꼼히 확인해야 합니다.
* **증분 아카이빙 패턴의 유용함:** 150개의 뉴스를 일괄로 백엔드에서 디코딩하려고 하면 구글의 429 차단에 걸렸을 것입니다. 로컬 DB 파일(`news.json`)을 메모리 캐시처럼 활용해 기존에 수집된 뉴스를 거르고, 새로 들어온 뉴스만 증분(Incremental) 루프로 처리하는 최적화 로직을 항상 디폴트 설계 모델로 고려하기로 했습니다.
