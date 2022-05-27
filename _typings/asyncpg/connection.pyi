import typing as t

from .protocol import Record
from .prepared_stmt import PreparedStatement

class Connection:
    """Base connection class."""

    async def prepare(
        self, query: str, *, timeout: float | None = ..., record_class: Record | None = ...
    ) -> PreparedStatement: ...
    async def execute(self, query: str, *args: t.Any, timeout: float | None = ...) -> str: ...
