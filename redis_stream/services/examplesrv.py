import logging
from redis_stream.service import BaseService


log = logging.getLogger("ExampleService")


class ExampleService(BaseService):
    """
    Example Service Callback to register in the Redis consumer service

    Args:
        ServiceCallback (_type_): _description_
    """
    async def execute(self, *args, **kwargs):

        message_id = args[0]
        message_data = args[1]
        log.info(f"Example Micro Service with Message ID: {message_id}, \
                 Message Data: {message_data}")
