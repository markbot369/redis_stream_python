from typing import Callable, Awaitable
import importlib.metadata

# from importlib.metadata import entry_points


class PluginManager():

    def __init__(self):
        self._plugins = {}
        entry_points = importlib.metadata.entry_points().\
            get("redis_stream_examples", [])
        # # TODO: Add a more pythonic way to do this
        for entry_point in entry_points:
            self._plugins[entry_point.name] = entry_point.load()

    def get_class(self, name):
        """
        Returns the plugin with the given name, or None if it does not exist.

        :param name: the name of the plugin to retrieve
        :type name: str
        :return: the plugin with the given name, or None if it does not exist
        :rtype: Plugin or None
        """
        return self._plugins[name]

    def get_service(self, name) -> Callable[..., Awaitable]:
        return self._plugins[name]()
