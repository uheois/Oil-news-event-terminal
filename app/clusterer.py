from datetime import timedelta
from time_utils import now_utc_naive
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from db import SessionLocal, NewsHeadline, Event
from embedder import loads_embedding
from config import (
    SIMILARITY_THRESHOLD, CLUSTER_WINDOW_MINUTES,
    CANDIDATE_SOURCES, CANDIDATE_WINDOW_MINUTES,
    CONFIRMED_SOURCES, CONFIRMED_WINDOW_MINUTES,
    STRONG_SOURCES, STRONG_WINDOW_MINUTES, RESEARCH_WINDOW_MINUTES,
)


def _sim(a, b) -> float:
    return float(cosine_similarity([a], [b])[0][0])


def calculate_strength(items, avg_similarity: float, llm_confidence: float = 0.0) -> float:
    """No hard source-tiering: all sources count equally.

    100점 만점:
    - unique source count: 40
    - time density: 25
    - semantic similarity: 20
    - LLM confidence: 15
    """
    n_sources = len({x.source for x in items})
    times = [x.published_at for x in items]
    spread_seconds = max((max(times) - min(times)).total_seconds(), 1) if len(times) > 1 else 90

    source_score = min(n_sources / 5, 1) * 40
    time_score = max(0, 1 - spread_seconds / (60 * 60 * 6)) * 25  # 30분 이내일수록 높음
    similarity_score = max(0, min(1, (avg_similarity - 0.60) / 0.35)) * 20
    confidence_score = max(0, min(1, llm_confidence)) * 15
    return round(source_score + time_score + similarity_score + confidence_score, 2)


def status_from_cluster(items) -> str:
    # GitHub Actions는 5분마다 깨어나는 batch 방식.
    # 5분/15분/30분 기준으로 빠르게 판정한다. 모든 소스는 동등하게 취급한다.
    unique_sources = len({x.source for x in items})
    times = [x.published_at for x in items]
    spread = max((max(times) - min(times)).total_seconds(), 1) if len(times) > 1 else 0

    if unique_sources >= STRONG_SOURCES and spread <= STRONG_WINDOW_MINUTES * 60:
        return "strong"
    if unique_sources >= CONFIRMED_SOURCES and spread <= CONFIRMED_WINDOW_MINUTES * 60:
        return "confirmed"
    if unique_sources >= CANDIDATE_SOURCES and spread <= CANDIDATE_WINDOW_MINUTES * 60:
        return "candidate"

    # candidate보다 느리지만 비슷한 이벤트는 연구 후보로 보존한다.
    if unique_sources >= CANDIDATE_SOURCES and spread <= RESEARCH_WINDOW_MINUTES * 60:
        return "research_candidate"
    return "weak"


def cluster_unassigned(window_minutes: int | None = None):
    if window_minutes is None:
        window_minutes = CLUSTER_WINDOW_MINUTES

    db = SessionLocal()
    cutoff = now_utc_naive() - timedelta(minutes=window_minutes)
    rows = db.query(NewsHeadline).filter(
        NewsHeadline.event_id == None,
        NewsHeadline.published_at >= cutoff,
    ).all()

    clusters = []
    for row in rows:
        emb = loads_embedding(row.embedding)
        placed = False
        for cluster in clusters:
            sims = [_sim(emb, loads_embedding(x.embedding)) for x in cluster]
            if max(sims) >= SIMILARITY_THRESHOLD:
                cluster.append(row)
                placed = True
                break
        if not placed:
            clusters.append([row])

    created = []
    for cluster in clusters:
        if len({x.source for x in cluster}) < 2:
            continue
        avg_sim = 1.0 if len(cluster) == 1 else float(np.mean([
            _sim(loads_embedding(cluster[i].embedding), loads_embedding(cluster[j].embedding))
            for i in range(len(cluster)) for j in range(i + 1, len(cluster))
        ]))
        if avg_sim < SIMILARITY_THRESHOLD:
            continue

        event = Event(
            first_seen=min(x.published_at for x in cluster),
            status=status_from_cluster(cluster),
            event_strength=calculate_strength(cluster, avg_sim),
        )
        db.add(event)
        db.flush()
        for h in cluster:
            h.event_id = event.id
        created.append(event.id)

    db.commit()
    db.close()
    return created
