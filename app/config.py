import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///energy_events.db")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
NEWS_POLL_SECONDS = int(os.getenv("NEWS_POLL_SECONDS", "60"))

# Internal timestamps are stored as UTC-naive for SQLite/yfinance compatibility.
# Dashboard/date labels are displayed in US Eastern Time with weekday.
DISPLAY_TIMEZONE = os.getenv("DISPLAY_TIMEZONE", "America/New_York")

# GitHub Actions is batch-based. Keep the event windows tight so market-moving
# headlines are detected quickly, while still saving all candidate events.
CLUSTER_WINDOW_MINUTES = int(os.getenv("CLUSTER_WINDOW_MINUTES", "60"))
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.74"))

# Current event status criteria:
# - candidate: 5 minutes / 2 similar sources
# - confirmed: 15 minutes / 3 similar sources
# - strong: 30 minutes / 4 similar sources
# - research_candidate: 60 minutes / 2 similar sources, saved for later analysis
CANDIDATE_SOURCES = int(os.getenv("CANDIDATE_SOURCES", "2"))
CANDIDATE_WINDOW_MINUTES = int(os.getenv("CANDIDATE_WINDOW_MINUTES", "5"))
CONFIRMED_SOURCES = int(os.getenv("CONFIRMED_SOURCES", "3"))
CONFIRMED_WINDOW_MINUTES = int(os.getenv("CONFIRMED_WINDOW_MINUTES", "15"))
STRONG_SOURCES = int(os.getenv("STRONG_SOURCES", "4"))
STRONG_WINDOW_MINUTES = int(os.getenv("STRONG_WINDOW_MINUTES", "30"))
RESEARCH_WINDOW_MINUTES = int(os.getenv("RESEARCH_WINDOW_MINUTES", "60"))

# 키워드 필터를 완전히 끄고 싶으면 .env 또는 GitHub env에 KEYWORD_FILTER=0
KEYWORD_FILTER = os.getenv("KEYWORD_FILTER", "1") != "0"
MAX_ENTRIES_PER_FEED = int(os.getenv("MAX_ENTRIES_PER_FEED", "40"))

WINDOWS = {
    "m30_before": -30 * 60,
    "m10_before": -10 * 60,
    "m1_before": -60,
    "t0": 0,
    "m1": 60,
    "m10": 10 * 60,
    "m30": 30 * 60,
    "h1": 60 * 60,
    "h2": 2 * 60 * 60,
    "h3": 3 * 60 * 60,
    "h6": 6 * 60 * 60,
    "h12": 12 * 60 * 60,
}
