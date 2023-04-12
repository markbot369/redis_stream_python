import redis
from redis_stream.service import RedisStreamReader


test_data = {
    'stream_key': 'mystream',
    'group_name': 'group1',
    'consumer_name': 'consumer1'
}


def test_redis_stream_connected():
    expected = True
    redis_stream_reader = RedisStreamReader(
        test_data['stream_key'],
        test_data['group_name'],
        test_data['consumer_name'])
    assert redis_stream_reader.is_connected() == expected


def test_redis_stream_reader():
    # Instantiate a Redis stream reader
    stream_key = test_data['stream_key']
    group_name = test_data['group_name']
    consumer_name = test_data['consumer_name']
    redis_stream_reader = RedisStreamReader(
        stream_key, group_name, consumer_name
    )

    # Create a test message
    message_data = {'foo': 'bar'}

    # Add the message to the Redis stream
    redis_client = redis.Redis()
    redis_client.xadd(stream_key, message_data)

    # Read the message from the Redis stream
    messages = list(redis_stream_reader.read())
    assert len(messages) == 1
    message = messages[0]

    # Check that the message data matches
    assert message[b'foo'] == b'bar'

    # Acknowledge the message
    redis_stream_reader.ack(message['message_id'])
