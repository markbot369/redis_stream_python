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
                 service=None,
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
        self._service = service
        self._server_config = server_config or {}
        self._redis = None

    async def connect_to_redis(self):
        """
        Connects to Redis using the specified Redis configuration.
        """
        host = self._server_config.get('host', 'localhost')
        port = self._server_config.get('port', 6379)
        self._redis = await aioredis.Redis.from_url(f"redis://{host}:{port}")
        log.info(f"Connected to Redis at {host}:{port}")

    async def consume(self, callback=None):
        """
        Reads messages from the stream in a consumer group asynchronously.
        """
        service = self._service or callback
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

        if service:
            for message_id, message_data in messages:
                # Process the message data with a callable.
                await service(message_id, message_data)
                log.debug(f"Message ID: {message_id}, \
                            Message Data: {message_data}")

    def ack(self, message_id):
        self._redis.xack(self._stream_name,
                         self._group_name,
                         message_id)

    def nack(self, message_id):
        self._redis.xack(self._stream_name,
                         self._group_name,
                         message_id,
                         False)

    async def start(self, callback=None):
        """
        Starts the asynchronous stream consumer.
        """
        await self.connect_to_redis()
        while True:
            await self.consume(callback)

    async def stop(self):
        """
        Stops the asynchronous stream consumer.
        """
        if self._redis:
            self._redis.close()
            # await self._redis_db.wait_closed()
        log.info('Closed Redis connection')

    def describe(self):
        return f'Stream: {self._stream_name} \
                Group: {self._group_name} \
                Consumer: {self._consumer_name}'
