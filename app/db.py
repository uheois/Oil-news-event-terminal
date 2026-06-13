from datetime import datetime
from time_utils import now_utc_naive
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from config import DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class NewsHeadline(Base):
    __tablename__ = "news_headlines"
    id = Column(Integer, primary_key=True)
    source = Column(String, nullable=False)
    title = Column(Text, nullable=False)
    url = Column(Text)
    published_at = Column(DateTime, nullable=False)
    embedding = Column(Text)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=True)

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True)
    first_seen = Column(DateTime, default=now_utc_naive)
    summary = Column(Text)
    oil_impact = Column(String, default="unclear")
    confidence = Column(Float, default=0.0)
    reason = Column(Text)
    event_strength = Column(Float, default=0.0)
    status = Column(String, default="candidate")
    classified = Column(Boolean, default=False)
    headlines = relationship("NewsHeadline")

class PriceReaction(Base):
    __tablename__ = "price_reactions"
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    symbol = Column(String, default="WTI")
    label = Column(String, nullable=False)
    target_time = Column(DateTime, nullable=False)
    price = Column(Float)
    return_pct = Column(Float)
    captured_at = Column(DateTime)


def init_db():
    Base.metadata.create_all(bind=engine)
