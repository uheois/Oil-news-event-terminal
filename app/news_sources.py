from datetime import datetime, timezone
from urllib.parse import quote_plus
import feedparser
from config import KEYWORD_FILTER, MAX_ENTRIES_PER_FEED


def google_news_rss(query: str) -> str:
    q = quote_plus(query)
    return f"https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"


# 기존 공개 RSS는 유지하고, Reuters/Bloomberg/FinancialJuice는 Google News site-search RSS로 추가.
# 정식 유료/로그인 API를 확보하면 같은 이름으로 connector만 교체하면 됨.
RSS_SOURCES = {
    # Existing public sources
    "Yahoo Finance Energy": "https://finance.yahoo.com/rss/sector/energy",
    "Investing Oil": "https://www.investing.com/rss/news_25.rss",
    "CNN Business": "http://rss.cnn.com/rss/money_latest.rss",
    "EIA": "https://www.eia.gov/rss/todayinenergy.xml",
    "IEA": "https://www.iea.org/rss/news.xml",
    "OPEC": "https://www.opec.org/opec_web/en/rss.xml",

    # Added broad sources via Google News RSS
    "Reuters Energy": google_news_rss("site:reuters.com oil OR crude OR energy OR OPEC OR Iran OR Fed"),
    "Reuters World": google_news_rss("site:reuters.com Iran OR Israel OR Russia OR Ukraine OR sanctions OR Hormuz OR Red Sea"),
    "Reuters Markets": google_news_rss("site:reuters.com markets Fed OR dollar OR inflation OR oil OR crude"),
    "Bloomberg Energy": google_news_rss("site:bloomberg.com oil OR crude OR energy OR OPEC OR Iran"),
    "Bloomberg Markets": google_news_rss("site:bloomberg.com markets Fed OR dollar OR inflation OR oil OR crude"),
    "FinancialJuice": google_news_rss("site:financialjuice.com oil OR crude OR Fed OR FOMC OR Iran OR OPEC"),
    "Investing Commodities": google_news_rss("site:investing.com commodities oil OR crude OR gold OR dollar"),
    "Investing Energy": google_news_rss("site:investing.com oil OR crude OR energy OR OPEC"),
}

MARKET_MOVING_KEYWORDS = [
    # Oil / energy
    "oil", "crude", "wti", "brent", "gasoline", "diesel", "jet fuel", "energy",
    "inventory", "inventories", "stockpile", "stockpiles", "draw", "build",
    "opec", "opec+", "eia", "iea", "production", "output", "supply", "demand",
    "refinery", "pipeline", "lng", "natural gas", "hormuz", "tanker",

    # Geopolitics
    "iran", "iraq", "israel", "gaza", "hamas", "hezbollah", "houthi", "saudi", "uae",
    "middle east", "red sea", "suez", "russia", "ukraine", "sanction", "sanctions",
    "war", "strike", "attack", "missile", "ceasefire", "peace", "trump", "tariff",

    # Macro / FX
    "fed", "fomc", "powell", "rate cut", "rate hike", "interest rate", "inflation",
    "cpi", "ppi", "nfp", "jobs report", "payrolls", "dollar", "usd", "treasury yields",
    "recession", "stimulus", "china", "china demand", "trade war",

    # Weather / disruption
    "hurricane", "storm", "shutdown", "outage", "explosion", "fire",
]


def _parse_dt(entry):
    if getattr(entry, "published_parsed", None):
        return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc).replace(tzinfo=None)
    if getattr(entry, "updated_parsed", None):
        return datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc).replace(tzinfo=None)
    return datetime.utcnow()


def _clean_google_news_title(title: str, source: str) -> str:
    # Google News RSS often returns: "Actual title - Reuters"
    suffixes = [" - Reuters", " - Bloomberg", " - Investing.com", " - Yahoo Finance", " - CNN"]
    for s in suffixes:
        if title.endswith(s):
            title = title[: -len(s)]
    return title.strip()


def _is_relevant(title: str) -> bool:
    if not KEYWORD_FILTER:
        return True
    text = title.lower()
    return any(k in text for k in MARKET_MOVING_KEYWORDS)


def fetch_latest_headlines() -> list[dict]:
    items = []
    seen = set()
    for source, url in RSS_SOURCES.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:MAX_ENTRIES_PER_FEED]:
                title = getattr(entry, "title", "").strip()
                if not title:
                    continue
                title = _clean_google_news_title(title, source)
                if not _is_relevant(title):
                    continue
                key = (source, title.lower())
                if key in seen:
                    continue
                seen.add(key)
                items.append({
                    "source": source,
                    "title": title,
                    "url": getattr(entry, "link", ""),
                    "published_at": _parse_dt(entry),
                })
        except Exception as e:
            print(f"source error: {source}: {e}")
            continue
    return items
