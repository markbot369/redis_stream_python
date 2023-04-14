from typing import Callable, Awaitable
import logging
import pytest

from redis_stream.plugin_manager import PluginManager


test_service = 'example_service'


@pytest.fixture
def plugin_manager():
    return PluginManager()


def test_plugin_manager_load_service(plugin_manager):
    service = plugin_manager.get_class(test_service)
    assert service.__name__ == "ExampleService"


@pytest.mark.asyncio
async def test_plugin_manager_run_service(plugin_manager, caplog):
    # Set up logging
    logger = logging.getLogger("ExampleService")
    logger.setLevel(logging.DEBUG)

    service: Callable[..., Awaitable] = plugin_manager.\
        get_service(test_service)
    await service('01', {})
    assert "Example Micro Service with Message ID: 01" in caplog.text
