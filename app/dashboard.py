import streamlit as st
import pandas as pd
import plotly.express as px
from db import SessionLocal, init_db, Event, NewsHeadline, PriceReaction
from collector import ingest_once
from time_utils import format_et

ORDER = ["m30_before", "m10_before", "m1_before", "t0", "m1", "m10", "m30", "h1", "h2", "h3", "h6", "h12"]
LABELS = {
    "m30_before":"T-30m", "m10_before":"T-10m", "m1_before":"T-1m", "t0":"T0",
    "m1":"+1m", "m10":"+10m", "m30":"+30m", "h1":"+1h", "h2":"+2h", "h3":"+3h", "h6":"+6h", "h12":"+12h"
}

st.set_page_config(page_title="Oil Event Intelligence Terminal", layout="wide")
init_db()
st.title("Oil Event Intelligence Terminal")
st.caption("All event times are displayed in US Eastern Time with weekday. Internal DB timestamps are UTC for compatibility.")

if st.button("Run one update now"):
    st.write(ingest_once())

db = SessionLocal()
events = db.query(Event).order_by(Event.first_seen.desc()).limit(200).all()

rows = [{
    "id": e.id,
    "first_seen_et": format_et(e.first_seen, with_seconds=True),
    "impact": e.oil_impact,
    "confidence": e.confidence,
    "strength": e.event_strength,
    "status": e.status,
    "summary": e.summary or "",
} for e in events]

df = pd.DataFrame(rows)
if df.empty:
    st.info("No events yet. Run the worker/GitHub Action or click 'Run one update now'.")
    db.close()
    st.stop()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Events", len(df))
c2.metric("Candidates+", int(df["status"].isin(["candidate", "confirmed", "strong", "research_candidate"]).sum()))
c3.metric("Confirmed/Strong", int(df["status"].isin(["confirmed", "strong"]).sum()))
c4.metric("Avg Strength", round(df["strength"].mean(), 1))

st.subheader("Recent Events")
status_options = ["candidate", "confirmed", "strong", "research_candidate", "weak"]
selected_statuses = st.multiselect(
    "Status filter",
    status_options,
    default=["candidate", "confirmed", "strong", "research_candidate"],
)
view_df = df[df["status"].isin(selected_statuses)] if selected_statuses else df
st.dataframe(view_df, use_container_width=True, hide_index=True)

if view_df.empty:
    st.warning("No events match the selected status filter.")
    db.close()
    st.stop()

selected = st.selectbox(
    "Select event",
    view_df["id"].tolist(),
    format_func=lambda x: f"#{x} - {view_df[view_df.id==x].iloc[0]['first_seen_et']} - {view_df[view_df.id==x].iloc[0]['summary'][:80]}"
)
event = db.query(Event).get(selected)

st.subheader(f"Event #{event.id}")
st.write({
    "first_seen_et": format_et(event.first_seen, with_seconds=True),
    "impact": event.oil_impact,
    "confidence": event.confidence,
    "strength": event.event_strength,
    "status": event.status,
    "summary": event.summary,
    "reason": event.reason,
})

st.markdown("### Clustered Headlines")
heads = db.query(NewsHeadline).filter_by(event_id=event.id).all()
for h in heads:
    published = format_et(h.published_at, with_seconds=True)
    st.markdown(f"- **{h.source}** · {published}: [{h.title}]({h.url})" if h.url else f"- **{h.source}** · {published}: {h.title}")

st.markdown("### Price Reaction")
reactions = db.query(PriceReaction).filter_by(event_id=event.id).all()
rdf = pd.DataFrame([{
    "symbol": r.symbol,
    "label": r.label,
    "target_time_et": format_et(r.target_time),
    "price": r.price,
    "return_pct": r.return_pct,
} for r in reactions])
if not rdf.empty:
    rdf["order"] = rdf["label"].apply(lambda x: ORDER.index(x) if x in ORDER else 999)
    rdf["time"] = rdf["label"].map(LABELS)
    rdf = rdf.sort_values(["symbol", "order"])
    st.dataframe(rdf[["symbol", "time", "target_time_et", "price", "return_pct"]], use_container_width=True, hide_index=True)
    for symbol in rdf["symbol"].unique():
        sdf = rdf[(rdf["symbol"] == symbol) & (rdf["return_pct"].notna())]
        if not sdf.empty:
            fig = px.line(sdf, x="time", y="return_pct", markers=True, title=f"{symbol} return from T0 (%)")
            st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No price reactions scheduled yet for this event.")

st.markdown("### Most Sensitive Events by 12h Absolute WTI Move")
all_reactions = db.query(PriceReaction).filter_by(symbol="WTI", label="h12").all()
impact_rows = []
for r in all_reactions:
    if r.return_pct is not None:
        ev = db.query(Event).get(r.event_id)
        impact_rows.append({
            "event_id": ev.id,
            "first_seen_et": format_et(ev.first_seen),
            "summary": ev.summary,
            "impact": ev.oil_impact,
            "status": ev.status,
            "strength": ev.event_strength,
            "abs_12h_move": abs(r.return_pct),
            "return_12h": r.return_pct,
        })
impact_df = pd.DataFrame(impact_rows).sort_values("abs_12h_move", ascending=False) if impact_rows else pd.DataFrame()
if not impact_df.empty:
    st.dataframe(impact_df.head(20), use_container_width=True, hide_index=True)
else:
    st.info("12h reaction data will appear after enough time has passed.")

db.close()
