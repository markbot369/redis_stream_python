from redis import asyncio as aioredis


class RedisService:
    """Base Redis service class that's connects to a Redis stream server."""
    def __init__(self, stream_name, queue_name,
                 server: str = 'localhost',
                 port: int = 6379):
        self._stream_name = stream_name
        self._queue_name = queue_name
        self._localhost = server
        self._port = port
        self._redis_db = None

    async def connect_to_redis(self):
        self._redis_db = await aioredis.create_redis_pool(
            f'redis://{self._localhost}:{self._port}'
        )

    async def write_to_queue(self, message):
        await self._redis_db.lpush(self._queue_name, message)

    async def read_from_stream(self):
        while True:
            message = await self._redis_db.xread(
                [self._stream_name],
                latest_ids=['>'],
                count=1,
                timeout=0
            )
            print(f'Received message from stream: {message}')
            await self.write_to_queue(message)

    async def start(self):
        await self.connect_to_redis()
        await self.read_from_stream()
