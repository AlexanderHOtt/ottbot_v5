# -*- coding=utf-8 -*-
"""Database models."""
import datetime
import typing as t

import asyncpg


class AttrRecord(asyncpg.Record):
    """An `asyncpg.Record` where attributes are accessible through '.' notation.

    print(Record.id)
    print(Record.name)
    """

    __tablename__: str

    def __getattr__(self, __name: str, /) -> t.Any:
        try:
            return self[__name]
        except Exception as e:
            raise AttributeError(*e.args) from e


class AutoRole(AttrRecord):
    """AutoRole model for database."""

    __tablename__ = "auto_roles"

    id: int
    guild_id: int
    role_id: int


class Currency(AttrRecord):
    """Currency model for database."""

    __tablename__ = "currency"

    id: int
    user_id: int
    balance: int
    bank: int
    last_daily: datetime.datetime


class User(AttrRecord):
    """User model for database."""

    __tablename__ = "users"

    id: int
    discord_id: int
    access_token: str
    refresh_token: str
    username: str
    discriminator: str
