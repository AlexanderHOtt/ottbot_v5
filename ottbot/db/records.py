# -*- coding=utf-8 -*-
"""Database models."""
import datetime
import typing as t

import asyncpg

__all__ = ("AutoRole", "Currency", "GuildConfig", "User", "Starboard")


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
    role_name: str


class Currency(AttrRecord):
    """Currency model for database."""

    __tablename__ = "currency"

    id: int
    user_id: int
    balance: int
    bank: int
    last_daily: datetime.datetime


class GuildConfig(AttrRecord):
    """GuildConfig model for database."""

    __tablename__ = "guild_config"

    id: int
    guild_id: int
    prefix: str
    welcome_channel_id: int | None
    welcome_mesage: str | None
    log_channel_id: int | None
    starboard_channel_id: int | None


class User(AttrRecord):
    """User model for database."""

    __tablename__ = "users"

    id: int
    discord_id: int
    access_token: str
    refresh_token: str
    username: str
    discriminator: str


class Starboard(AttrRecord):
    """Starboard entry model."""

    __tablename__ = "starboard"

    id: int
    original_channel_id: int
    original_message_id: int
    sent_channel_id: int
    sent_message_id: int
