import redis


class RedisStreamReader:
    def __init__(self, stream_key, group_name, consumer_name, 
                 server='localhost', port=6379):
        self.redis_client = redis.Redis.from_url(f"redis://{server}:{port}")
        self.stream_key = stream_key
        self.group_name = group_name
        self.consumer_name = consumer_name
        # self.redis_client.xgroup_create(self.stream_key, self.group_name, mkstream=True)
        self.consumer = self.redis_client.xreadgroup(
            self.group_name,
            self.consumer_name,
            {self.stream_key: ">"})

    def is_connected(self):
        return self.redis_client.ping()

    def read(self):
        while True:
            messages = self.consumer[0][1]
            if messages:
                yield from messages

    def ack(self, message_id):
        self.redis_client.xack(self.stream_key, self.group_name, message_id)

    def nack(self, message_id):
        self.redis_client.xack(self.stream_key, self.group_name, message_id, False)
