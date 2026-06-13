from datetime import timedelta, datetime
from time_utils import now_utc_naive
import yfinance as yf
from db import SessionLocal, Event, PriceReaction
from config import WINDOWS

SYMBOLS = {"WTI": "CL=F", "Brent": "BZ=F", "USDKRW": "KRW=X"}


def get_price(symbol: str, target_time: datetime):
    ticker = SYMBOLS[symbol]
    start = target_time - timedelta(days=1)
    end = target_time + timedelta(days=1)
    interval = "1m" if abs((now_utc_naive() - target_time).total_seconds()) < 7 * 24 * 3600 else "1h"
    data = yf.download(ticker, start=start, end=end, interval=interval, progress=False, auto_adjust=False)
    if data.empty:
        return None
    data = data.reset_index()
    time_col = "Datetime" if "Datetime" in data.columns else "Date"
    data["diff"] = (data[time_col].dt.tz_localize(None) - target_time).abs()
    row = data.sort_values("diff").iloc[0]
    close_value = row["Close"]
    if hasattr(close_value, "iloc"):
        close_value = close_value.iloc[0]
    return float(close_value)


def schedule_reactions_for_event(event_id: int):
    db = SessionLocal()
    event = db.query(Event).get(event_id)
    for symbol in SYMBOLS:
        for label, offset in WINDOWS.items():
            exists = db.query(PriceReaction).filter_by(event_id=event_id, symbol=symbol, label=label).first()
            if not exists:
                db.add(PriceReaction(event_id=event_id, symbol=symbol, label=label, target_time=event.first_seen + timedelta(seconds=offset)))
    db.commit(); db.close()


def update_due_reactions():
    db = SessionLocal()
    due = db.query(PriceReaction).filter(PriceReaction.price == None, PriceReaction.target_time <= now_utc_naive()).all()
    for r in due:
        price = get_price(r.symbol, r.target_time)
        if price is None:
            continue
        r.price = price
        r.captured_at = now_utc_naive()
        t0 = db.query(PriceReaction).filter_by(event_id=r.event_id, symbol=r.symbol, label="t0").first()
        if t0 and t0.price and r.label != "t0":
            r.return_pct = (price / t0.price - 1) * 100
    db.commit(); db.close()
