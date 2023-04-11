from redis import asyncio as aioredis


class RedisClient:
    """
    Base Redis client class that's connects to a Redis
     stream server and writes to a specified stream.
    """
    def __init__(self, stream_name,
                 server: str = 'localhost',
                 port: int = 6379):
        self._stream_name = stream_name
        self._localhost = server
        self._port = port
        self._redis_db = None

    async def connect_to_redis(self):
        self._redis_db = await aioredis.Redis.from_url(
            f'redis://{self._localhost}:{self._port}'
        )

    async def write_to_stream(self, message):
        await self._redis_db.xadd(self._stream_name, message)


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
        self._redis_db = await aioredis.Redis.from_url(
            f'redis://{self._localhost}:{self._port}'
        )

    async def write_to_queue(self, message):
        await self._redis_db.lpush(self._queue_name, message)

    async def read_from_stream(self):
        while True:
            message = await self._redis_db.xread(
                streams={self._stream_name: 0},
                # [self._stream_name],
                latest_ids=['>'],
                count=1
                # timeout=0
            )
            print(f'Received message from stream: {message}')
            # await self.write_to_queue(message)

    async def start(self):
        await self.connect_to_redis()
        await self.read_from_stream()



import asyncio
import aioredis

class AsyncRedisStreamConsumer:
    def __init__(self, stream_name, group_name, consumer_name, last_delivered_id='$', count=1, redis_config=None):
        """
        Initializes a AsyncRedisStreamConsumer object with the specified stream, group, and consumer names, and Redis configuration.
        """
        self.stream_name = stream_name
        self.group_name = group_name
        self.consumer_name = consumer_name
        self.last_delivered_id = last_delivered_id
        self.count = count
        self.redis_config = redis_config or {}
        self.redis_pool = None

    async def consume(self):
        """
        Reads messages from the stream in a consumer group asynchronously.
        """
        if not self.redis_pool:
            self.redis_pool = await aioredis.create_redis_pool((self.redis_config.get('host', 'localhost'),
                                                                 self.redis_config.get('port', 6379),
                                                                 self.redis_config.get('db', 0)))
        try:
            stream_data = await self.redis_pool.xreadgroup(self.group_name,
                                                           self.consumer_name,
                                                           {self.stream_name: self.last_delivered_id},
                                                           count=self.count,
                                                           timeout=0)
        except asyncio.CancelledError:
            self.redis_pool.close()
            await self.redis_pool.wait_closed()
            raise

        if not stream_data:
            return None

        stream_id, messages = stream_data[0]
        self.last_delivered_id = stream_id

        for message_id, message_data in messages:
            # Process the message data
            print(f"Message ID: {message_id}, Message Data: {message_data}")

    async def start(self):
        """
        Starts the asynchronous stream consumer.
        """
        while True:
            await self.consume()

    async def stop(self):
        """
        Stops the asynchronous stream consumer.
        """
        if self.redis_pool:
            self.redis_pool.close()
            await self.redis_pool.wait_closed()

if __name__ == '__main__':
    stream_name = 'mystream'
    group_name = 'mygroup'
    consumer_name = 'myconsumer'
    last_delivered_id = '$' # start reading from the latest message
    count = 10
    redis_config = {'host': 'localhost', 'port': 6379, 'db': 0}

    stream_consumer = AsyncRedisStreamConsumer(stream_name, group_name, consumer_name, last_delivered_id, count, redis_config)

    async def run_consumer():
        await stream_consumer.start()

    try:
        asyncio.run(run_consumer())
    except KeyboardInterrupt:
        asyncio.run(stream_consumer.stop())
