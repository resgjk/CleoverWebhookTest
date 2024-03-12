import os

from dotenv import load_dotenv

from sqlalchemy.engine import URL

from apscheduler.schedulers.asyncio import AsyncIOScheduler


load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
WEBHOOK_DOMAIN = os.getenv("WEBHOOK_DOMAIN")
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH")


postgres_url = URL.create(
    "postgresql+asyncpg",
    username=DB_USER,
    host=DB_HOST,
    database=DB_NAME,
    port=DB_PORT,
    password=DB_PASSWORD,
)
scheduler = AsyncIOScheduler()
