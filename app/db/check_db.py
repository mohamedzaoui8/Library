import asyncio

from sqlalchemy import text

from app.db.session import engine


async def main():
    async with engine.connect() as connection:
        result = await connection.execute(text("SELECT 1"))
        print(result.scalar_one())

    await engine.dispose()


asyncio.run(main())