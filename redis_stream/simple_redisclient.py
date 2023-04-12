import redis


class RedisClient:
    def __init__(self, host, port, password, stream_key):
        self.host = host
        self.port = port
        self.password = password
        self.stream_key = stream_key
        self.redis_client = redis.Redis(host=self.host, port=self.port, password=self.password)

    def is_connected(self):
        return self.redis_client.ping()

    def publish_message(self, message):
        self.redis_client.xadd(self.stream_key, message)

    def consume_messages(self, consumer_group, consumer_name,
                         last_id='>', count=1):
        messages = self.redis_client.xreadgroup(
            groupname=consumer_group,
            consumername=consumer_name,
            streams={self.stream_key: last_id},
            count=count,
            block=0
        )
        return messages

    def ack(self, message_id):
        self.redis_client.xack(self.stream_key, self.group_name, message_id)

    def nack(self, message_id):
        self.redis_client.xack(self.stream_key, self.group_name, message_id, False)
