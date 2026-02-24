import asyncio
from dotenv import load_dotenv
from app.logging_config import setup_logging
from app.voice_server import start_server
from app import db

async def main():
    load_dotenv()
    setup_logging()
    await db.init_db_pool()
    await start_server()

if __name__ == "__main__":
    asyncio.run(main())
