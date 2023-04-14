import argparse
from redis_stream.simple_redisclient import RedisStreamReader


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('stream_key', help='Redis stream key to read from')
    parser.add_argument('group_name', help='Consumer group name')
    parser.add_argument('consumer_name', help='Consumer name')
    parser.add_argument('--server', default='localhost',
                        help='Redis server host')
    parser.add_argument('--port', default=6379, type=int,
                        help='Redis server port')
    return parser.parse_args()


def main():
    args = parse_args()
    reader = RedisStreamReader(args.stream_key,
                               args.group_name,
                               args.consumer_name,
                               server=args.server,
                               port=args.port)
    if reader.is_connected():
        for message in reader.read():
            # process the message
            reader.ack(message['id'])
    else:
        print('Error: Redis client is not connected')


if __name__ == '__main__':
    main()
