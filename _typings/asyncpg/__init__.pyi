# -*- coding=utf-8 -*-
"""asyncpg stubs"""
import typing as t
import types as tp
import collections.abc as c

import asyncio
from .pool import PoolConnectionProxy
from .connection import Connection
from .protocol import Record

__all__ = ["PoolConnectionProxy", "Connection", "Record", "PoolAcquireContext", "Pool", "create_pool"]

class PoolAcquireContext:
    async def __aenter__(self) -> PoolConnectionProxy: ...
    async def __aexit__(
        self,
        exec_type: t.Type[BaseException] | None = ...,
        exec: BaseException | None = ...,
        tb: t.Type[tp.TracebackType] | None = ...,
    ) -> None: ...

class Pool:
    """A Connection to a database."""
    def acquire(self, *, timeout: float | None = ...) -> PoolAcquireContext: ...
    async def close(self) -> None: ...
    async def execute(self, query: str, *args: t.Any, timeout: float | None = ...): ...
    async def executemany(self, command: str, args: t.Any, *, timeout: float | None = ...): ...

async def create_pool(
    dsn: str | None = ...,
    *args: t.Any,
    min_size: int = 10,
    max_size: int = 10,
    max_queries: int = 50000,
    max_inactive_connection_lifetime: float = 300.0,
    setup: c.Callable[[PoolConnectionProxy], None] | None = ...,
    init: c.Callable[[Connection], None] | None = ...,
    loop: asyncio.AbstractEventLoop | None = ...,
    connection_class: t.Type[Connection] = ...,
    record_class: t.Type[Record] = ...,
    **connect_kwargs: str | int,
) -> Pool: ...
