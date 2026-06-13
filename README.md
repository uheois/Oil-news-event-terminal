# Oil Event Intelligence Terminal

A personal event-driven intelligence system for oil, energy, geopolitics, and macroeconomic news.(draft)

The system continuously collects headlines, clusters similar stories into events, and tracks market reactions in:

- WTI Crude Oil
- Brent Crude Oil
- USD/KRW

## Features

- Automated news collection via GitHub Actions
- Event clustering from multiple sources
- Candidate / Confirmed / Strong event detection
- Event strength scoring
- Historical event database
- Price reaction tracking

## News Sources

- Reuters Energy
- Reuters World
- Reuters Markets
- Yahoo Finance
- Investing.com
- EIA
- IEA
- OPEC

## Event Levels

- Candidate
- Confirmed
- Strong
- Research Candidate

## Market Reaction Windows

- T-30m
- T-10m
- T-1m
- T0
- T+1m
- T+10m
- T+30m
- T+1h
- T+2h
- T+3h
- T+6h
- T+12h

## Database

- news_headlines
- events
- price_reactions

## Automation

GitHub Actions runs every 5 minutes and updates the event database automatically.

## Status

Work in progress.

Current focus:

- Event detection quality
- High-impact news recognition
- Price reaction analytics
- Dashboard visualization

프로젝트: Oil News Event Terminal

현재 상태:
- GitHub repo: Oil-news-event-terminal
- GitHub Actions로 5분 cron 수집 시도 중
- SQLite DB: energy_events.db
- 테이블: news_headlines, events, price_reactions
- Reuters Energy / Reuters World / Reuters Markets / FinancialJuice / Investing Commodities / Investing Energy / EIA / IEA / OPEC 수집 중
- 약 300개 headlines 수집 확인
- events는 현재 1개 생성됨

문제점:
- Trump / Iran / Powell / FOMC 같은 중요 뉴스가 단일 기사면 이벤트 생성 안 됨
- 현재 클러스터 기준이 너무 엄격함
- HIGH_IMPACT_TERMS 기반 단일 기사 candidate 로직 추가 예정

향후 작업:
1. 이벤트 생성 기준 완화
2. HIGH_IMPACT_TERMS 추가
3. candidate / confirmed / strong 재설계
4. WTI / Brent / USDKRW 반응 저장 검증
5. GitHub Pages 기반 대시보드 구축 (Streamlit 보류)

