import argparse
import asyncio
from redis_stream.service import RedisService


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--stream', default='mystream',
                        help='Redis stream name')
    parser.add_argument('--queue', default='myqueue',
                        help='Redis queue name')
    parser.add_argument('--server', default='localhost',
                        help='Redis server address')
    parser.add_argument('--port', default=6379,
                        help='Redis server port')
    return parser.parse_args()


async def main():
    """_summary_
    Server for running the Redis service

    ```bash
    python myscript.py --stream mycustomstream --queue mycustomqueue
    ```
    """
    args = parse_arguments()
    redis_service = RedisService(args.stream, args.queue, )
    await redis_service.start()


if __name__ == '__main__':
    asyncio.run(main())
