from db import SessionLocal, NewsHeadline, init_db
from news_sources import fetch_latest_headlines
from embedder import embed_text, dumps_embedding
from clusterer import cluster_unassigned
from classifier import classify_event
from price_worker import schedule_reactions_for_event, update_due_reactions


def ingest_once():
    init_db()
    db = SessionLocal()
    inserted = 0
    fetched = fetch_latest_headlines()
    for item in fetched:
        exists = db.query(NewsHeadline).filter_by(source=item["source"], title=item["title"]).first()
        if exists:
            continue
        h = NewsHeadline(
            source=item["source"],
            title=item["title"],
            url=item.get("url"),
            published_at=item["published_at"],
            embedding=dumps_embedding(embed_text(item["title"])),
        )
        db.add(h)
        inserted += 1
    db.commit(); db.close()

    event_ids = cluster_unassigned()
    for eid in event_ids:
        classify_event(eid)
        schedule_reactions_for_event(eid)
    update_due_reactions()
    return {"fetched_headlines": len(fetched), "inserted_headlines": inserted, "new_events": len(event_ids)}

if __name__ == "__main__":
    print(ingest_once())
