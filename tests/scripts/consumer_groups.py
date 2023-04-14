"""
Base script for preparing the Redis consumer groups and consumers for the 
testings.
"""
import redis

# Redis stream configuration
stream_name = 'mystream'
max_length = 1000

# Redis client configuration
redis_config = {'host': 'localhost', 'port': 6379, 'db': 0}

# Create Redis client
redis_client = redis.Redis(**redis_config)

# Create Redis stream
redis_client.xadd(stream_name, {'message': 'hello'})

# Create consumer groups
group_names = ['group1', 'group2']
for group_name in group_names:
    redis_client.xgroup_create(stream_name, group_name, id='0')

# Create consumers
consumer_names = ['consumer1', 'consumer2', 'consumer3']
for consumer_name in consumer_names:
    # Register consumer in each group
    for group_name in group_names:
        redis_client.xgroup_createconsumer(
            stream_name,
            group_name,
            consumer_name)

# Consume messages
while True:
    for group_name in group_names:
        # Read messages from group
        messages = redis_client.xreadgroup(
            group_name,
            'consumer',
            {stream_name: '>'},
            count=10)
        for message in messages:
            # Process message
            print(f"Group: {group_name}, Message: {message[1]}")
