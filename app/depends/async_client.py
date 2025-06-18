from httpx import AsyncClient


async def make_request():
    async with AsyncClient() as client:
        yield client