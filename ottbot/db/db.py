# -*- coding=utf-8 -*-
"""Simple Database driver for the postgres database."""
import asyncio
import typing as t

import aiofiles
import asyncpg
from asyncpg.pool import PoolConnectionProxy

from ottbot import config as config_

_P = t.ParamSpec("_P")
_R = t.TypeVar("_R")

Self = t.TypeVar("Self", bound="AsyncPGDatabase")


class AsyncPGDatabase:
    """Wrapper class for AsyncPG Database access."""

    __slots__ = ("calls", "user", "password", "db", "host", "port", "schema", "pool")

    def __init__(self, config: config_.DatabaseConfig) -> None:
        """Create a new Database handler."""
        self.calls: int = 0
        self.user: str = config.user
        self.password: str = config.password
        self.db: str = config.database
        self.host: str = config.host
        self.port: int = config.port
        self.schema: str = "./ottbot/data/static/schema.sql"

    async def connect(self) -> None:
        """Opens a connection pool."""
        self.pool = await asyncpg.create_pool(
            user=self.user,
            host=self.host,
            port=self.port,
            database=self.db,
            password=self.password,
            loop=asyncio.get_running_loop(),
        )

        await self.scriptexec(self.schema)

    async def close(self) -> None:
        """Closes the connection pool."""
        await self.pool.close()

    @staticmethod
    def with_connection(
        func: t.Callable[t.Concatenate[Self, PoolConnectionProxy, _P], t.Awaitable[_R]]
    ) -> t.Callable[t.Concatenate[Self, _P], t.Awaitable[_R]]:
        """A decorator used to acquire a connection from the pool."""

        async def wrapper(_self: Self, *args: _P.args, **kwargs: _P.kwargs) -> _R:
            async with _self.pool.acquire() as conn:
                _self.calls += 1
                return await func(_self, conn, *args, **kwargs)

        return wrapper

    @with_connection
    async def fetch(self, conn: PoolConnectionProxy, q: str, *values: t.Any) -> t.Optional[t.Any]:
        """Read 1 field of applicable data.

        SELECT username FROM users WHERE id=1
        """
        query = await conn.prepare(q)
        return await query.fetchval(*values)

    @with_connection
    async def row(self, conn: PoolConnectionProxy, q: str, *values: t.Any) -> asyncpg.Record | None:
        """Read 1 row of applicable data.

        SELECT * FROM users WHERE id=1
        """
        query = await conn.prepare(q)
        return await query.fetchrow(*values)

    @with_connection
    async def rows(
        self,
        conn: PoolConnectionProxy,
        q: str,
        *values: t.Any,
    ) -> t.Optional[t.List[t.Iterable[t.Any]]]:
        """Read all rows of applicable data.

        SELECT * FROM users
        """
        query = await conn.prepare(q)
        if data := await query.fetch(*values):
            return [*map(lambda r: tuple(r.values())[0], data)]

        return None

    @with_connection
    async def column(
        self,
        conn: PoolConnectionProxy,
        q: str,
        *values: t.Any,
    ) -> t.List[t.Any]:
        """Read a single column of applicable data.

        SELECT username FROM users
        """
        query = await conn.prepare(q)
        return [r[0] for r in await query.fetch(*values)]

    @with_connection
    async def execute(
        self,
        conn: PoolConnectionProxy,
        q: str,
        *values: t.Any,
    ) -> None:
        """Execute a write operation on the database.

        UPDATE users SET id=10 WHERE id=1
        """
        query = await conn.prepare(q)
        await query.fetch(*values)

    @with_connection
    async def executemany(
        self,
        conn: PoolConnectionProxy,
        q: str,
        values: t.List[t.Iterable[t.Any]],
    ) -> None:
        """Execute a write operation for each set of values."""
        query = await conn.prepare(q)
        await query.executemany(values)

    @with_connection
    async def scriptexec(self, conn: PoolConnectionProxy, path: str) -> None:
        """Execute an sql script at a given path."""
        async with aiofiles.open(path, "r", encoding="utf-8") as script:
            await conn.execute((await script.read()))
