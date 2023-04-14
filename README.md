# Making a Redis Stream Client Example in Python

## Introduction

Microservice architecture has become a popular approach to developing software applications that are scalable, maintainable, and flexible. One of the challenges of microservice architecture is managing the flow of data between services, which can become complex as the number of services and interactions between them grows.

One solution to this challenge is to use message queues to decouple services, allowing them to communicate asynchronously and reducing the risk of service failures and downtime. Redis streams are a type of message queue that are particularly well-suited for microservice architecture.

Redis streams allow multiple producers to write messages to a stream, which can then be read by multiple consumers. This allows services to communicate in a scalable and efficient way, with messages being delivered in the order they are received. Redis streams also support message acknowledgment and automatic message retention, making it easy to implement reliable message processing in microservices.

In this article, we'll explore how to use Python and the aioredis module to connect to a Redis stream and write to a defined queue. We'll demonstrate how to encapsulate this functionality in a Python class, and how to make it into a CLI application with command-line arguments. By the end of this article, you'll have a better understanding of how to use Redis streams in your own microservice architecture projects.

## Redis Stream Client

## Redis Stream Client Example

The following code defines a class called `RedisStreamReader`, which is responsible for consuming messages from a Redis stream using a consumer group:

```python
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

```

The `__init__` method initializes the `RedisStreamReader` instance with the `stream_key`, `group_name`, `consumer_name`, `server`, and `port` parameters. It creates a Redis client instance using the `redis.Redis.from_url()` method with the provided server and port. It also sets the `stream_key`, `group_name`, and `consumer_name` instance variables. The `xgroup_create()` method is commented out and not used, but it can be used to create a consumer group for the stream if it does not already exist. The `xreadgroup()` method is used to read messages from the stream using the consumer group, and the resulting messages are stored in the consumer instance variable.

The `is_connected()` method checks if the Redis client is connected by sending a ping request to the Redis server.

The `read()` method is a generator that continuously reads messages from the stream using the consumer group. It loops indefinitely and checks for new messages in the consumer instance variable. If there are messages, it yields them using the yield from statement.

The `ack()` method acknowledges a message by sending an acknowledgement (ACK) to the stream using the `xack()` method with the message ID, stream key, and consumer group name.

The `nack()` method negatively acknowledges a message by sending a negative acknowledgement (NACK) to the stream using the `xack()` method with the message ID, stream key, consumer group name, and a False flag.

To call the above code in a CLI application, you can create an instance of the `RedisStreamReader` class with the appropriate parameters(we provide some example), and then use its methods to read and acknowledge messages from the stream. For example:

```python
import argparse
from redis_stream.simple_redisclient import RedisStreamReader


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('stream_key', help='Redis stream key to read from')
    parser.add_argument('group_name', help='Consumer group name')
    parser.add_argument('consumer_name', help='Consumer name')
    parser.add_argument('--server', default='localhost', help='Redis server host')
    parser.add_argument('--port', default=6379, type=int, help='Redis server port')
    return parser.parse_args()


def main():
    args = parse_args()
    reader = RedisStreamReader(args.stream_key, args.group_name, args.consumer_name,
                                server=args.server, port=args.port)
    if reader.is_connected():
        for message in reader.read():
            # process the message
            reader.ack(message['id'])
    else:
        print('Error: Redis client is not connected')


if __name__ == '__main__':
    main()
```

In this example, we define a main() function that parses the command line arguments using the argparse module, creates an instance of RedisStreamReader, and then loops through the messages returned by the read() method, processing each message and acknowledging it using the ack() method. If the Redis client is not connected, an error message is printed.

To run the CLI application, you can execute the Python script with the appropriate command line arguments. For example:

```bash
python myapp.py mystream mygroup myconsumer --server redis.mycompany.com --port 6379
```

## Create some tests to see how this Redis service works

These tests cover the basic functionality of the Redis client, ensuring that messages can be published to the stream and consumed by a consumer group.
The following provided code is a set of unit tests written using the pytest testing framework. The tests are designed to test the functionality of the `RedisClient` class, which is defined in the `simple_redisclient.py` module.

```python
import pytest
from redis_stream.simple_redisclient import RedisClient


stream_name = 'mystream'

@pytest.fixture
def redis_client():
    return RedisClient('localhost', 6379, None, stream_name)


def test_publish_message(redis_client):
    # Clear all the data in the  test stream
    # Use XTRIM to remove all messages from the stream
    redis_client.redis_client.xtrim(stream_name, maxlen=0)

    message = {'name': 'Bob', 'age': '25'}
    redis_client.publish_message(message)
    result = redis_client.redis_client.xread({redis_client.stream_key: 0},
                                             count=1)
    res_msg = {key.decode('utf-8'): value.decode('utf-8')
               for key, value in result[0][1][0][1].items()}
    assert res_msg == message


def test_consume_messages(redis_client):
    consumer_group = 'group1'
    consumer_name = 'consumer1'
    last_id = '>'
    count = 3

    redis_client.redis_client.xtrim(stream_name, maxlen=0)
    # publish some messages to the stream
    messages = [
        {'name': 'Charlie', 'age': '35'},
        {'name': 'David', 'age': '40'},
        {'name': 'Eve', 'age': '45'}
    ]
    for message in messages:
        redis_client.publish_message(message)

    # consume messages from the stream
    result = redis_client.consume_messages(
        consumer_group,
        consumer_name,
        last_id=last_id,
        count=count)

    res_message = {key.decode('utf-8'): value.decode('utf-8')
                   for key, value in result[0][1][0][1].items()}
    assert len(result) == 1
    assert len(result[0][1]) == count
    assert res_message == messages[0]

```

The first test, test_publish_message(), tests the publish_message() method of the RedisClient class. This method is used to publish a message to a Redis stream. In the test, the stream is first cleared using the xtrim() method, and then a message is published using the publish_message() method. The test then reads the message from the stream using the xread() method and checks that the message is the same as the one that was published.

The second test, test_consume_messages(), tests the consume_messages() method of the RedisClient class. This method is used to consume messages from a Redis stream using a consumer group. In the test, the stream is first cleared using the xtrim() method, and then three messages are published to the stream using the publish_message() method. The test then consumes the messages from the stream using the consume_messages() method and checks that the messages are the same as the ones that were published.

Both tests use the assert statement to check that the expected results are returned. If the expected results are not returned, the tests will fail and an error message will be displayed. This allows the developer to identify and fix any issues with the code.

The test then is invocated with the calling the PyTest command bellow:

```bash
pytest -v tests/test_simple_client.py
```

## Creating a Redis stream consumer service for using in a microservice environment

In a microservice environment we need to provide a service that can consume messages(events) from a Redis stream and can react to this event and run some function asociated with such event.

It’s possible to have multiple consumer groups as well as regular consumers that are not part of any group, all consuming messages at the  same time.

In the following figure, there are two different consumer groups (“Customer Care Application” and “Payment Application”) as well as a regular consumer 
(like an admin "Dashboard Service") that are all consuming the messages.

--------------------------------
TODO: Insert the figure here
--------------------------------

Thats the base principle of using Redis Streams for a microservice environment. All the consumer groups and regular consumers are consuming the messages(events) that are important for their inner context functionality.

## Redis Stream Service

In this section we will create a Redis Stream service that can consume messages from a Redis stream. The service will consume messages from the Redis stream in an asynchronous manner.

### Redis stream asynchronous consumer
Now we will create a Redis Stream consumer in an asynchronous form to consume messages from a Redis stream in a consumer group.
The following code defines a class called `AsyncRedisStreamConsumer`. The purpose of this class is to provide an asynchronous interface for consuming messages from a Redis stream in a defined consumer group.

```python
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

```

The constructor takes several arguments, including the name of the stream, the name of the consumer group, the name of the consumer, and a configuration object for the Redis server. By default, the consumer starts consuming messages from the most recent message in the stream (indicated by last_delivered_id='>') and it will read a single message at a time (indicated by count=1).

The class has several methods:

- `connect_to_redis`: This method connects to the Redis server using the configuration specified in the constructor.
- `consume`: This method reads messages from the stream in a consumer group asynchronously. If a callback function is provided, it will be invoked with each message. Otherwise, it will simply log the message. The method retrieves the messages from the Redis server using the xreadgroup() method of the Redis library. The method returns a tuple containing the stream ID and the messages that were read.
- `ack`: This method acknowledges the consumption of a message with the given ID. It does so using the xack() method of the Redis library.
- `nack`: This method negates the consumption of a message with the given ID. It does so using the xack() method of the Redis library and passing False as the last parameter.
- `start`: This method starts the consumer. It first connects to the Redis server, and then repeatedly calls consume() in a loop until it is stopped. If a callback function is provided, it will be invoked with each message.
- `stop`: This method stops the consumer. It simply closes the Redis connection.
- `describe` This method returns a string that provides information about the stream, the consumer group, and the consumer used for the messages consumption.

The code abstracts away the details of connecting to the Redis server and reading messages from the stream, and it provides a simple interface for acknowledging and negating the consumption of messages.

## Making a plugin system for consuming messages from a Redis stream

## Redis Stream Server

To make this code into a CLI application, we use the argparse module to parse command-line arguments. The parse_arguments function defines two optional arguments, `--stream`, with default values of "mystream", respectively. The main function calls parse_arguments to retrieve the command-line arguments, and then creates an instance of the RedisService class with these arguments.

## Redis Stream Server in Docker

### Redis Stream Server Docker Image

### Redis Stream Client DockerCompose File
