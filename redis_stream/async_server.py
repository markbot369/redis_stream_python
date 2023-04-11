import asyncio
import logging
from redis_stream.async_service import AsyncRedisStreamConsumer


log = logging.getLogger("Redis async server")


redis_default_config = {
    'host': 'localhost',
    'port': 6379,
    'db': 0,
    'stream_name': 'mystream',
    'group_name': 'group1',
    'consumer_name': 'consumer1'
}


def serve(
        stream_name,
        group_name,
        consumer_name,
        redis_config=redis_default_config,
        last_delivered_id='>',
        count=1):
    stream_consumer = AsyncRedisStreamConsumer(
        stream_name,
        group_name,
        consumer_name,
        redis_config,
        last_delivered_id,
        count)

    async def run_consumer():
        log.info(f"Consumer started for stream name: {stream_name}, Group name: {group_name}, Consumer name: {consumer_name} ")
        await stream_consumer.start()

    try:
        asyncio.run(run_consumer())
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
        # parser.add_argument('--queue', default='myqueue',
        #                     help='Redis queue name')
        parser.add_argument('--server', default='localhost',
                            help='Redis server address')
        parser.add_argument('--port', default=6379,
                            help='Redis server port')
        return parser.parse_args()

    args = parse_arguments()
    redis_default_config['host'] = args.server
    redis_default_config['port'] = args.port
    serve(args.stream, args.group, args.consumer,
          redis_config=redis_default_config,
          count=args.count,
          last_delivered_id=args.lastid)


if __name__ == '__main__':
    main()
