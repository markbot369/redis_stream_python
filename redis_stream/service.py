"""Creates a basic Python callable as a microservice for running inside the 
Redis stream consumer.
"""
from typing import Any


class BaseService:
    """
    Creates a basic Python callable for running inside the 
    Redis consumer service.
    """
    async def __call__(self, *args: Any, **kwds: Any) -> Any:
        """Call the object as a function, 
        passing *args and **kwds to self.execute().

        Args:
            *args: Positional arguments to pass to self.execute().
            **kwds: Keyword arguments to pass to self.execute().

        Returns:
            The result of calling self.execute(*args, **kwds).
        """
        await self.execute(*args, **kwds)

    async def execute(self, *args: Any, **kwds: Any) -> Any:
        """
        Executes the function with the given arguments and keyword arguments.

        Args:
            *args: Positional arguments to pass to the function.
            **kwds: Keyword arguments to pass to the function.

        Returns:
            The return value of the function.

        """
        pass
