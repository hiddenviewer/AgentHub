# 🤖 AgentHub

> **AI 에이전트(AI Agent / Agentic AI) 최신 동향 수집 및 학습자료 아카이빙 플랫폼**

**AgentHub**는 급변하는 인공지능 에이전트 분야의 최신 기사와 개발 트렌드를 실시간에 준하여 자동으로 수집하고, 학습에 핵심적인 가이드, 도구 및 논문을 일목요연하게 큐레이션하여 제공하는 오픈소스 정적 아카이브 사이트입니다.

GitHub Pages로 호스팅되며, 백엔드 서버 없이 GitHub Actions 스크립트만을 활용하여 100% 무료 및 반영구적으로 자동 업데이트됩니다.

---

## ✨ 핵심 기능

1. **최신 뉴스 자동 수집 (News Aggregator)**
   - 12시간마다 Google News RSS를 연동하여 국내외 **"AI 에이전트"**, **"Agentic AI"** 핵심 키워드 기사를 자동 수집합니다.
   - 링크 중복 제거 및 최신성(발행일)을 반영하여 상위 150개의 뉴스를 아카이빙합니다.
   - 검색창을 통해 제목 및 출처 언론사를 실시간으로 필터링하고, 국내/해외 뉴스 별로 분류해 볼 수 있습니다.

2. **학습 자료 정리 (Curated Resources)**
   - AI 에이전트 개념 가이드, 핵심 논문, 개발 프레임워크(LangGraph, CrewAI, AutoGen 등)를 카테고리별로 정돈하여 제공합니다.
   - 사용자가 학습 과정에서 유용한 자료를 직접 추가하거나 수정하여 자신만의 위키(Wiki)로 발전시킬 수 있습니다.

3. **프리미엄 UI/UX 디자인**
   - 글래스모피즘(Glassmorphism)과 네온 그라데이션 광원을 기반으로 한 다크 모드 중심의 현대적이고 고급스러운 디자인 레이아웃을 제공합니다.
   - 반응형 레이아웃을 통해 모바일, 태블릿, PC 기기 환경에 완벽히 대응합니다.

---

## 📂 디렉토리 구조

```text
AgentHub/
├── .github/
│   └── workflows/
│       └── update_news.yml    # GitHub Actions 수집 & 배포 자동화
├── data/
│   ├── news.json              # 수집된 최신 뉴스 데이터
│   └── resources.json         # 카테고리별 에이전트 공부 자료
├── scripts/
│   └── collect_news.py        # RSS 수집 및 중복 처리 Python 크롤러
├── index.html                 # 메인 웹페이지
├── styles.css                 # 글래스모피즘/다크모드 스타일시트
├── app.js                     # 프런트엔드 데이터 렌더링 & 필터링 로직
└── README.md                  # 프로젝트 설명 파일
```

---

## 🛠️ 동작 방식 & 배포 설정

### 1. 뉴스 데이터 업데이트 프로세스
1. **GitHub Actions Workflow**가 매일 12시간 주기(한국 시간 오전 9시, 오후 9시)로 작동합니다.
2. `scripts/collect_news.py`가 작동하여 신규 뉴스를 크롤링하고 기존 `data/news.json` 데이터와 머지(Merge)합니다.
3. 데이터가 변경되면 `github-actions[bot]`이 자동으로 해당 변경분을 GitHub 저장소에 커밋 및 푸시합니다.
4. 변경 사항이 리포지토리에 반영되면서 GitHub Pages가 즉시 자동 빌드되어 사용자에게 항상 최신 데이터의 화면을 제공합니다.

### 2. 최초 배포 방법
1. 이 프로젝트 코드를 GitHub 저장소에 push합니다.
2. **GitHub Repository Settings** > **Pages** 탭으로 이동합니다.
3. **Build and deployment** 항목의 **Source**를 `Deploy from a branch`로 설정하고 브랜치를 `main` (또는 수집 커밋을 푸시할 브랜치), 폴더를 `/ (root)`로 선택한 뒤 저장합니다.
4. 이후 저장소 메인 화면 우측의 `github-pages` 배포가 성공하면 `https://<YOUR-USERNAME>.github.io/AgentHub/` 주소로 사이트 접속이 가능해집니다.

---

## 🚀 로컬 테스트 방법

로컬에서 수집 스크립트 실행 및 웹 페이지를 테스트하려면 아래 순서대로 진행할 수 있습니다.

1. **뉴스 수집 스크립트 로컬 실행**
   ```bash
   python3 scripts/collect_news.py
   ```

2. **로컬 웹 서버 구동**
   ```bash
   # Python 기본 웹서버 실행
   python3 -m http.server 8000
   ```
   이후 브라우저에서 `http://localhost:8000`에 접속하여 사이트 화면을 테스트해 보실 수 있습니다.
