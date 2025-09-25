from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    ENV = os.getenv("ENV", "development")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    SCHEDULE_INTERVAL_SECONDS = int(os.getenv("SCHEDULE_INTERVAL_SECONDS", "60"))

    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sync.db")

    # Shopee
    SHOPEE_PARTNER_ID = os.getenv("SHOPEE_PARTNER_ID")
    SHOPEE_PARTNER_KEY = os.getenv("SHOPEE_PARTNER_KEY")
    SHOPEE_SHOP_ID = os.getenv("SHOPEE_SHOP_ID")
    SHOPEE_API_BASE = os.getenv("SHOPEE_API_BASE", "https://partner.shopeemobile.com/api/v2")

    # Loyverse
    LOYVERSE_API_BASE = os.getenv("LOYVERSE_API_BASE")
    LOYVERSE_TOKEN = os.getenv("LOYVERSE_TOKEN")

    MAX_WORKERS = int(os.getenv("MAX_WORKERS", "5"))

settings = Settings()
