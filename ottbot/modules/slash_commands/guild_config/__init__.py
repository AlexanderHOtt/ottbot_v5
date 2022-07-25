# -*- coding=utf-8 -*-
"""Guild configuration related commands."""
import hikari

from ottbot.db import AsyncPGDatabase, GuildConfig


async def get_guild_config(guild_id: int | hikari.Snowflake, db: AsyncPGDatabase) -> GuildConfig:
    """Returns the config for a guild, it will create one if it does not exist."""
    await db.execute(
        "INSERT INTO guild_config (guild_id) VALUES ($1) ON CONFLICT DO NOTHING", guild_id, record_cls=GuildConfig
    )
    config = await db.row("SELECT * FROM guild_config WHERE guild_id = $1", guild_id, record_cls=GuildConfig)
    assert config is not None, "Database error creating guild config"
    return config
