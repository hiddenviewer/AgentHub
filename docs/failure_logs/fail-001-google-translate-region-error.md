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
2. **크롤링 시점의 실제 URL 디코딩 도입 (절반의 성공):**
   * 문제의 원인이 '구글 뉴스 도메인의 중간 주소'이기 때문에, 이를 해결하려면 최종 본문 기사가 실린 원본 사이트 도메인(예: `techcrunch.com`)의 다이렉트 URL을 구해야 함을 깨달았습니다.
   * `googlenewsdecoder` 라이브러리를 연동해 크롤링 단계에서 base64 및 `batchexecute` 프로토콜을 통과하여 디코딩된 최종 진짜 도메인 주소를 얻도록 `collect_news.py`를 개편했습니다.
3. **구글 번역기의 리다이렉트 우회 및 번역 엔진 파파고로 교체 (최종 성공):**
   * 원본 URL을 획득했음에도 불구하고, `translate.google.com/translate` API는 접속 시점에 사용자의 브라우저를 프록시 도메인인 `[orig-domain].translate.goog`로 강제 리다이렉트하여 웹 페이지를 번역하려고 합니다.
   * 이 리다이렉트된 도메인이 여전히 로컬 리전 보안 정책에 걸려 `This translation service isn't available in your region` 에러를 뿜는 현상이 재현되었습니다.
   * 이에 구글 번역기 대신, 한국 사용자 접근성이 극대화되고 한글 번역 퀄리티가 훨씬 높은 **네이버 파파고 웹 번역 서비스**(`papago.naver.com`)로 프런트엔드 연결 링크를 변경하여 리전 제한 문제를 완벽하게 회피(Bypass)하는 데 최종 성공했습니다.

## 4. 교훈 및 방지 대책 (Lessons Learned & Action Items)
* **타사 서비스 연동 시의 블랙박스 리프레시 주의:** 타사 번역 툴처럼 동적으로 URL을 재구성하고 프록시하는 서비스는 내부적으로 어떤 강제 리다이렉션을 유발할지 예측하기 힘듭니다.
* **로컬 친화적 대안 모색:** 다국어 글로벌 서비스가 필요하지 않은 환경이라면, 국내 사용자에게 특화되고 리전 에러가 발생하지 않는 로컬 대기업 API/서비스(네이버 등)를 대안으로 적극 고려해야 함을 배웠습니다.
* **방어 코드 작성:** 복호화에 실패한 원시 구글 뉴스 URL에 대해서는 애초에 번역 버튼이 노출되지 않도록 `app.js`에서 링크 형식 필터링을 한 겹 더 씌워 안정성을 높였습니다.
