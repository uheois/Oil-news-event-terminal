# GitHub Actions 자동 수집 설정

이 버전은 로컬에서 24시간 켜두는 방식이 아니라, GitHub Actions가 **5분마다** 깨어나 한 번 수집하고 종료하는 방식입니다.

## 현재 이벤트 기준

모든 candidate/confirmed/strong 이벤트는 DB에 저장됩니다. status는 필터링용 태그입니다.

- candidate: 최근 5분 내 유사 뉴스 2개 이상
- confirmed: 최근 15분 내 유사 뉴스 3개 이상
- strong: 최근 30분 내 유사 뉴스 4개 이상
- research_candidate: 최근 60분 내 유사 뉴스 2개 이상

모든 뉴스 소스는 기본적으로 동등하게 취급합니다. Reuters/Bloomberg/FinancialJuice/Yahoo/CNN/Investing/OPEC/EIA/IEA를 소스 등급으로 크게 차별하지 않습니다.

## 시간 기준

- DB 내부 저장: UTC
- 화면 표시: 미국 동부시간(ET, America/New_York)
- 날짜 표시: 요일 포함, 예: `Fri 2026-06-13 09:07 EDT`

## 업로드 순서

```powershell
git init
git add .
git commit -m "initial oil event terminal"
```

GitHub에서 새 repo 생성 후:

```powershell
git branch -M main
git remote add origin https://github.com/YOUR_ID/YOUR_REPO.git
git push -u origin main
```

## GitHub Actions 켜기

Repo → Actions 탭 → workflow 허용.

수동 실행:

Actions → collect-oil-news-events → Run workflow

## OpenAI API 키 선택사항

OpenAI 분류를 쓰려면:

Repo → Settings → Secrets and variables → Actions → New repository secret

이름:

```text
OPENAI_API_KEY
```

값: 본인 OpenAI API key

키가 없으면 fallback keyword classifier로 동작합니다.

## 로컬에서 대시보드 보기

GitHub에서 최신 DB를 pull 받은 뒤:

```powershell
cd "C:\Users\임혜연\OneDrive\바탕 화면\oil_daily"
.\venv\Scripts\Activate.ps1
cd .\oil_news\energy_news_event_terminal
python -m streamlit run app\dashboard.py
```
