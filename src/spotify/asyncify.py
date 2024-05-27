import asyncio
from functools import partial
from typing import Any, Callable, Coroutine, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def asyncify(func: Callable[P, R]) -> Callable[P, Coroutine[Any, Any, R]]:
    async def async_wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, partial(func, *args, **kwargs))

    return async_wrapper  # type: ignore
