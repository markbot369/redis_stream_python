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

## Create some tests to see how this Redis service works

These tests cover the basic functionality of the Redis client, ensuring that messages can be published to the stream and consumed by a consumer group.
For init the test we are using the PyTest library. Import the `pytest` module and the `RedisClient` class.

```python
import pytest
from redis_stream.simple_redisclient import RedisClient
```

In this example, the `redis_client` fixture creates an instance of the RedisClient class and connects to a Redis server. The fixture also flushes the Redis database and closes the connection after each test.

```python
@pytest.fixture
def redis_client():
    return RedisClient('localhost', 6379, None, stream_name)

```

Then we can test the `publish_message` method and the `consume_messages` method with the following code:

```python
def test_publish_message(redis_client):
    # Clear all the data in the  test stream
    # Use XTRIM to remove all messages from the stream
    redis_client.redis_client.xtrim(stream_name, maxlen=0)

    message = {'name': 'Bob', 'age': '25'}
    redis_client.publish_message(message)
    result = redis_client.redis_client.xread({redis_client.stream_key: 0}, count=1)
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

The test then is invocated with the calling the PyTest command bellow:

```bash
pytest -v tests/test_simple_client.py
```

To create a service that continuously listens for new messages on a Redis stream, you can use the Redis xreadgroup command with the block option set to a non-zero value. This will block the client until new messages are available on the stream. Here's an example of a Python script that implements this:

```python
import redis

class RedisStreamListener:
    def __init__(self, host, port, stream_key, consumer_group, consumer_name):
        self.host = host
        self.port = port
        self.password = password
        self.stream_key = stream_key
        self.consumer_group = consumer_group
        self.consumer_name = consumer_name
        self.redis_client = redis.Redis(host=self.host, port=self.port)

        # Create the consumer group if it doesn't exist
        self.redis_client.xgroup_create(self.stream_key, self.consumer_group, id='0', mkstream=True)

    def listen(self):
        while True:
            messages = self.redis_client.xreadgroup(
                group_name=self.consumer_group,
                consumer_name=self.consumer_name,
                streams={self.stream_key: '>'},
                count=1,
                block=0
            )
            if messages:
                for message in messages[0][1]:
                    # Process the message here
                    print(f"Received message: {message[1]}")
                    self.redis_client.xack(self.stream_key, self.consumer_group, message[0])

```

When using the XREADGROUP command to read messages from a stream and process them in a distributed fashion across multiple consumers the XACK command is used to acknowledge that a consumer has processed one or more messages from a stream.

After a consumer has processed a message, it should call the XACK command to tell Redis that the message has been processed and can be removed from the stream. If the XACK command is not called, the message will remain in the stream and may be delivered to another consumer.

We can add a method for our client to acknowled the message by calling the XACK command. The method takes the message ID and the consumer group name. The method returns `True` if the message was acknowledged, `False` if the message was not acknowledged, and `None` if the message was not acknowledged.

Here is the code for such method:

```python
def ack(self, message_id):
        self.redis_client.xack(self.stream_key, self.group_name, message_id)

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

## Redis Stream Server

To make this code into a CLI application, we use the argparse module to parse command-line arguments. The parse_arguments function defines two optional arguments, `--stream` and `--queue`, with default values of mystream and myqueue, respectively. The main function calls parse_arguments to retrieve the command-line arguments, and then creates an instance of the RedisService class with these arguments.

Finally, we use the `asyncio.run` function to run the main function asynchronously. This allows the service to run indefinitely, reading from the Redis stream and writing to the queue.

## Redis Stream Server in Docker

### Redis Stream Server Docker Image

### Redis Stream Client DockerCompose File
