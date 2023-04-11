import pytest
import asyncio
from redis_stream.service import RedisService


@pytest.fixture
async def redis_service():
    service = RedisService(stream_name='test_stream', queue_name='test_queue')
    await service.connect_to_redis()
    yield service
    await service._redis_db.flushdb()
    await service._redis_db.close()


# @pytest.mark.asyncio
# async def test_write_to_queue(redis_service):
#     message = 'test message'
#     await redis_service.write_to_queue(message)
#     result = await redis_service._redis_db.lrange(redis_service._queue_name, 0, -1)
#     assert result == [message.encode()]


@pytest.mark.asyncio
async def test_read_from_stream(redis_service, capsys):
    message = {'test_stream': [(b'1-0', {b'message': b'test message'})]}
    await redis_service._redis_db.xadd('test_stream', message)
    await asyncio.sleep(0.1)
    captured = capsys.readouterr()
    assert 'Received message from stream' in captured.out
