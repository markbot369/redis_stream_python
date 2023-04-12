import asyncio
import logging
from redis import asyncio as aioredis


log = logging.getLogger(__name__)


class AsyncRedisStreamConsumer:
    def __init__(self,
                 stream_name,
                 group_name,
                 consumer_name,
                 server_config=None,
                 last_delivered_id='>',
                 count=1):
        """
        Initializes a AsyncRedisStreamConsumer object with the specified 
        stream, group, and consumer names, and Redis configuration.
        """
        self._stream_name = stream_name
        self._group_name = group_name
        self._consumer_name = consumer_name
        self._last_delivered_id = last_delivered_id
        self._count = count
        self._server_config = server_config or {}
        # self._stream_name = redis_config.get(stream_name, 'mystream')
        # self._group_name = redis_config.get(group_name, 'group1')
        # self._consumer_name = redis_config.get(consumer_name, 'consumer1')
        self._redis_db = None

    async def connect_to_redis(self):
        """
        Connects to Redis using the specified Redis configuration.
        """
        host = self._server_config.get('host', 'localhost')
        port = self._server_config.get('port', 6379)
        self._redis = await aioredis.Redis.from_url(f"redis://{host}:{port}")
        log.info(f"Connected to Redis at {host}:{port}")

    async def consume(self):
        """
        Reads messages from the stream in a consumer group asynchronously.
        """
        try:
            stream_data = await self._redis.xreadgroup(
                groupname=self._group_name,
                consumername=self._consumer_name,
                streams={self._stream_name: self._last_delivered_id},
                count=self._count)
        except asyncio.CancelledError:
            self._redis.close()
            await self._redis.wait_closed()
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
        await self.connect_to_redis()
        while True:
            await self.consume()

    async def stop(self):
        """
        Stops the asynchronous stream consumer.
        """
        if self._redis:
            self._redis.close()
            # await self._redis_db.wait_closed()
        log.info('Closed Redis connection')
