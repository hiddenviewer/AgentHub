# 🤖 Guidelines for AI Agents (AGENTS.md)

이 문서는 AI 코딩 에이전트(예: Antigravity, Claude, Cursor 등)가 **AgentHub** 프로젝트에 참여하여 기능을 추가하거나 버그를 고칠 때 준수해야 하는 엔지니어링 표준과 지식 성장 가이드라인을 정의합니다.

---

## 🏗️ 1. 프로젝트 아키텍처 개요

* **프런트엔드:** 정적 HTML/CSS/Vanilla JS (`index.html`, `styles.css`, `app.js`)
* **데이터베이스:** 서버리스 정적 파일 (`data/news.json`, `data/resources.json`)
* **백엔드 (수집기):** 파이썬 자동 크롤링 스크립트 (`scripts/collect_news.py`)
* **자동화 및 배포:** GitHub Actions (`.github/workflows/update_news.yml`) 및 GitHub Pages

---

## 💡 2. 지식 성장 및 기록 구조 (중요)

이 프로젝트는 새로운 기능을 개발하고 실패를 겪으며 지식이 스스로 축적되는 성장형 리포지토리를 지향합니다. 중대한 설계 변경이 있거나 트러블슈팅을 거쳤을 때는 코드를 고치기 전에 **반드시 아래 가이드라인에 맞춰 문서를 기록**해야 합니다.

### A. 기술 결정 기록 (ADR)
* **목적:** 주요 라이브러리 도입, UI 아키텍처 개편 등 설계적 결정을 내린 이유와 장단점을 기록합니다.
* **위치:** `docs/decision_records/`
* **규칙:** [docs/decision_records/README.md](docs/decision_records/README.md)의 템플릿 양식에 따라 새 ADR 파일을 생성하고, 목록에 추가합니다.

### B. 실패 및 장애 기록 (Failure Logs)
* **목적:** 개발 중 혹은 배포 후 발생한 기술적 문제, 버그, 연동 실패, 성능 저하 등과 그 해결법을 솔직하게 기록합니다.
* **위치:** `docs/failure_logs/`
* **규칙:** [docs/failure_logs/README.md](docs/failure_logs/README.md)의 템플릿 양식에 따라 새 실패 기록 파일을 작성하고, 목록에 추가합니다.

---

## 🛠️ 3. 에이전트 개발 행동 규칙

### 🎨 UI 및 스타일 가이드라인 (styles.css)
* 라이트 모드 테마를 기본으로 합니다. 
* 테마의 색상 체계는 `:root`에 정의된 CSS Custom Properties 변수들(`--bg-primary`, `--accent-gradient` 등)을 엄격히 활용해야 하며, 하드코딩된 색상값 사용을 금지합니다.
* 카드 UI는 글래스모피즘(`backdrop-filter: blur()`)을 기반으로 하고, 그림자 효과를 부드럽고 가볍게 유지합니다.

### 🔌 뉴스 수집 크롤러 규칙 (collect_news.py)
* Google News RSS 피드 수집 시, 보안 및 리프레시 리다이렉트 링크를 원본 기사 주소로 디코딩하기 위해 `googlenewsdecoder` 라이브러리를 사용합니다.
* **증분 수집 필수:** 구글의 429(Too Many Requests) 차단을 예방하기 위해, 기존 `news.json`에 저장된 뉴스 제목과 비교하여 **새로 업데이트된 기사들만 골라 복호화(디코딩) 루프**를 돌려야 합니다.
* 디코딩 시에는 안정성을 위해 기사당 최소 1초 이상의 지연(`time.sleep(1)`)을 부여하고, 1회 최대 디코딩 한계(안전장치 25개)를 넘지 마십시오.

### 🚀 배포 및 워크플로우 제약사항
* GitHub Actions 파일(`.github/workflows/...`)을 수정하는 커밋은 깃허브 보안 정책에 따라 AI 에이전트의 OAuth API 토큰 권한으로 원격 저장소에 푸시(Push)가 되지 않고 리젝될 수 있습니다.
* 워크플로우 수정 커밋을 작성했을 경우, 에이전트는 푸시 에러에 대응하여 사용자에게 **직접 본인의 터미널 환경에서 `git push -f`를 실행할 것**을 정중하게 요청하여야 합니다.
