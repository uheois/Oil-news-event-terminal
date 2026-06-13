import json
from config import OPENAI_API_KEY
from db import SessionLocal, Event, NewsHeadline
from clusterer import calculate_strength

try:
    from openai import OpenAI
except Exception:
    OpenAI = None


def _fallback_classify(headlines: list[str]) -> dict:
    text = " ".join(headlines).lower()
    bullish_terms = ["attack", "strike", "sanction", "shutdown", "disruption", "draw", "cut", "hormuz", "war", "hurricane"]
    bearish_terms = ["ceasefire", "peace", "inventory build", "surplus", "output increase", "demand weak", "calls off"]
    b = sum(t in text for t in bullish_terms)
    s = sum(t in text for t in bearish_terms)
    if b > s:
        impact = "bullish"
    elif s > b:
        impact = "bearish"
    else:
        impact = "neutral"
    return {
        "event_summary": headlines[0][:180] if headlines else "",
        "oil_impact": impact,
        "confidence": 0.55,
        "reason": "Fallback keyword heuristic. Add OPENAI_API_KEY for LLM context classification."
    }


def classify_event(event_id: int) -> dict:
    db = SessionLocal()
    event = db.query(Event).get(event_id)
    headlines = db.query(NewsHeadline).filter(NewsHeadline.event_id == event_id).all()
    lines = [f"{h.source}: {h.title}" for h in headlines]

    if OPENAI_API_KEY and OpenAI is not None:
        client = OpenAI(api_key=OPENAI_API_KEY)
        prompt = f"""
Classify these clustered breaking-news headlines for crude oil futures.
Do not rely on isolated keywords. Pay attention to old vs new events, negation, reversal, supply impact, demand impact, sanctions, inventory, USD/Fed effects, and geopolitical escalation/de-escalation.

Headlines:
{chr(10).join('- ' + x for x in lines)}

Return JSON only:
{{
  "event_summary": "short summary",
  "oil_impact": "bullish | bearish | neutral | unclear",
  "confidence": 0.0,
  "reason": "short reason"
}}
"""
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            response_format={"type": "json_object"},
        )
        data = json.loads(res.choices[0].message.content)
    else:
        data = _fallback_classify(lines)

    event.summary = data.get("event_summary", "")
    event.oil_impact = data.get("oil_impact", "unclear")
    event.confidence = float(data.get("confidence", 0) or 0)
    event.reason = data.get("reason", "")
    event.classified = True
    event.event_strength = calculate_strength(headlines, 0.85, event.confidence)
    db.commit()
    db.close()
    return data
