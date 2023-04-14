import asyncio
import logging
from redis_stream.plugin_manager import PluginManager
from redis_stream.async_redisconsumer import AsyncRedisStreamConsumer


log = logging.getLogger("Redis async server")

plugins = PluginManager()

redis_default_config = {
    'host': 'localhost',
    'port': 6379,
    'db': 0,
    'stream_name': 'mystream',
    'group_name': 'group1',
    'consumer_name': 'consumer1'
}


def create_consumers(stream_name, group_name, consumer_name,
                     redis_config=redis_default_config,
                     last_delivered_id='>', services=[],
                     count=1):
    consumers = []
    for service in services:
        pluged_service = plugins.get_service(service)
        consumers.append(AsyncRedisStreamConsumer(stream_name,
                                                  group_name,
                                                  consumer_name,
                                                  redis_config,
                                                  last_delivered_id,
                                                  pluged_service,
                                                  count))
    return consumers


async def run_consumer(stream_consumer: AsyncRedisStreamConsumer = None):
    log.info(f"Consumer started for {stream_consumer.describe()}")
    await stream_consumer.start()


def serve(stream_name,
          group_name,
          consumer_name,
          redis_config=redis_default_config,
          last_delivered_id='>',
          services=[],
          count=1):

    stream_consumers = create_consumers(
        stream_name,
        group_name,
        consumer_name,
        redis_config,
        last_delivered_id,
        services,
        count
    )
    for stream_consumer in stream_consumers:
        try:
            asyncio.run(run_consumer(stream_consumer))
        except KeyboardInterrupt:
            asyncio.run(stream_consumer.stop())


def main():
    """_summary_
    Server for running the Redis service

    ```bash
    python myscript.py --stream mycustomstream --queue mycustomqueue
    ```
    """
    import argparse

    logging.basicConfig(level=logging.INFO)

    def parse_arguments():
        parser = argparse.ArgumentParser()
        parser.add_argument('--stream', default='mystream',
                            help='Redis stream name')
        parser.add_argument('--group', default='group1',
                            help='Redis group name')
        parser.add_argument('--consumer', default='consumer1',
                            help='Redis group consumer name')
        parser.add_argument('--count', default=1,
                            help='Redis group consumer name')
        parser.add_argument('--lastid', default='>',
                            help='Redis group consumer name')
        parser.add_argument('--server', default='localhost',
                            help='Redis server address')
        parser.add_argument('--port', default=6379,
                            help='Redis server port')
        parser.add_argument('--services', default=['example_service'],
                            help='Services to run when a message(event) \
                                is received')
        return parser.parse_args()

    args = parse_arguments()
    redis_default_config['host'] = args.server
    redis_default_config['port'] = args.port
    serve(args.stream, args.group, args.consumer,
          redis_config=redis_default_config,
          count=args.count,
          services=args.services,
          last_delivered_id=args.lastid)


if __name__ == '__main__':
    main()
