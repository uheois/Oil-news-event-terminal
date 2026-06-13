import time
from collector import ingest_once
from config import NEWS_POLL_SECONDS

while True:
    try:
        print(ingest_once())
    except Exception as e:
        print("worker error:", e)
    time.sleep(NEWS_POLL_SECONDS)
