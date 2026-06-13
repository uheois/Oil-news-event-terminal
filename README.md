# Oil Event Intelligence Terminal v3 — GitHub Actions batch mode

이 버전은 GitHub Actions에서 10분마다 자동 실행되도록 `.github/workflows/collect.yml`이 포함되어 있습니다.

GitHub 기준:

- candidate: 최근 10분 내 유사 뉴스 2개 이상
- confirmed: 최근 30분 내 유사 뉴스 3개 이상
- strong: 최근 60분 내 유사 뉴스 5개 이상
- research_candidate: RSS 지연을 고려해 최근 24시간 내 유사 뉴스 2개 이상

자세한 설정은 `GITHUB_ACTIONS_SETUP.md`를 보세요.

---

# Oil Event Intelligence Terminal

에너지/지정학/거시 뉴스 헤드라인을 수집하고, 의미적으로 유사한 기사들을 클러스터링한 뒤, 원유 선물 영향(`bullish / bearish / neutral / unclear`)과 시장 반응을 기록하는 MVP입니다.

## v2 변경점

- 기존 Yahoo / Investing / CNN / EIA / IEA / OPEC 유지
- Reuters / Bloomberg / FinancialJuice / Investing Energy·Commodities 검색 RSS 추가
- 소스별 등급 차별 최소화: 모든 매체는 기본적으로 동일하게 카운트
- Event Strength는 `매체 수 + 시간 집중도 + 의미 유사도 + LLM confidence` 중심
- RSS 테스트용 클러스터 윈도우 기본값을 6시간으로 확대
- 원유뿐 아니라 Fed/FOMC/Trump/Iran/Russia/Ukraine/USD/CPI/NFP 같은 거시·지정학 키워드 포함

## Event Strength

100점 만점:

- unique source count: 40
- time density: 25
- semantic similarity: 20
- LLM confidence: 15

## 이벤트 상태

- `candidate`: 90초 내 2개 이상 유사 보도
- `confirmed`: 3분 내 3개 이상 유사 보도
- `strong`: 10분 내 5개 이상 유사 보도
- `research_candidate`: RSS처럼 늦게 들어오는 소스에서 6시간 내 2개 이상 유사 보도

## 가격 저장 구간

`T-30m, T-10m, T-1m, T0, +1m, +10m, +30m, +1h, +2h, +3h, +6h, +12h`

대상: WTI, Brent, USD/KRW

## 실행

```powershell
cd "C:\Users\임혜연\OneDrive\바탕 화면\oil_daily"
.\venv\Scripts\Activate.ps1
cd .\oil_news\energy_news_event_terminal
python -m streamlit run app\dashboard.py
```

워커:

```powershell
cd "C:\Users\임혜연\OneDrive\바탕 화면\oil_daily"
.\venv\Scripts\Activate.ps1
cd .\oil_news\energy_news_event_terminal
python app\run_worker.py
```

## 설정

`.env.example`을 `.env`로 복사해서 필요시 수정합니다.

```env
OPENAI_API_KEY=
NEWS_POLL_SECONDS=60
SIMILARITY_THRESHOLD=0.76
CLUSTER_WINDOW_MINUTES=360
KEYWORD_FILTER=1
MAX_ENTRIES_PER_FEED=25
```

`OPENAI_API_KEY`가 없으면 fallback 임베딩/분류기로 실행됩니다. 진짜 문맥 판단은 OpenAI API 키를 넣는 쪽이 좋습니다.

## 주의

Bloomberg/Reuters/FinancialJuice의 완전한 실시간 속보는 보통 공식 유료 API, 로그인 세션, 터미널 export, 또는 별도 connector가 필요합니다. 현재 v2는 공개적으로 접근 가능한 RSS/Google News RSS 기반 테스트 connector입니다.


## v4 Notes

- GitHub Actions schedule: every 5 minutes.
- Event criteria tightened:
  - candidate: 5 minutes / 2 similar sources
  - confirmed: 15 minutes / 3 similar sources
  - strong: 30 minutes / 4 similar sources
  - research_candidate: 60 minutes / 2 similar sources
- Candidate events are saved, not discarded.
- Dashboard displays event/headline/reaction times in US Eastern Time with weekday.
- Internal DB timestamps remain UTC for compatibility with yfinance and GitHub runners.
