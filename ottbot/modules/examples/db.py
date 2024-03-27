# -*- coding=utf-8 -*-
"""Example database usage."""
import tanjun

from ottbot.db import AsyncPGDatabase
from ottbot.db.records import GuildConfig
from ottbot.utils.funcs import build_loaders

component, load_component, unload_component = build_loaders()


@component.with_slash_command
@tanjun.as_slash_command("example_db", "Example database usage.", default_to_ephemeral=True)
async def cmd_example_database(
    ctx: tanjun.abc.SlashContext, db: AsyncPGDatabase = tanjun.inject(type=AsyncPGDatabase)
) -> None:
    """Example database usage."""
    if ctx.guild_id is None:
        return

    guild_config = await db.row("SELECT * from guild_config WHERE guild_id = $1", ctx.guild_id, record_cls=GuildConfig)
    await ctx.respond(f"The current guild prefix is {guild_config.prefix if guild_config else 'not assigned yet'}")
