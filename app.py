import time
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from sync import SyncService
from settings import settings
from db import engine
from models import Base
from utils import logger

# ensure tables exist (for quick start). In production, use alembic migrations.
Base.metadata.create_all(bind=engine)

svc = SyncService()
scheduler = BackgroundScheduler()

def job():
    logger.info("Starting sync job")
    svc.run_once()
    logger.info("Finished sync job")

scheduler.add_job(job, "interval", seconds=settings.SCHEDULE_INTERVAL_SECONDS, max_instances=1)
scheduler.start()

try:
    logger.info("Sync service started. Press Ctrl+C to exit.")
    while True:
        time.sleep(10)
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()
    logger.info("Scheduler stopped.")
