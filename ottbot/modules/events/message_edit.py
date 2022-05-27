# -*- coding=utf-8 -*-
"""Message edit event listener."""

import difflib
import logging

import hikari
import tanjun

from ottbot.db import AsyncPGDatabase, GuildConfig
from ottbot.utils.funcs import build_loaders

component, load_component, unload_component = build_loaders()
logger = logging.getLogger(__name__)


@component.with_listener(hikari.GuildMessageUpdateEvent)
async def lsnr_guild_message_edit(
    event: hikari.GuildMessageUpdateEvent,
    bot: hikari.GatewayBot = tanjun.inject(type=hikari.GatewayBot),
    db: AsyncPGDatabase = tanjun.inject(type=AsyncPGDatabase),
) -> None:
    """On member join event listener."""
    if not event.is_human:
        return
    logger.info(f"Message Edit in {event.guild_id}")

    if (
        guild_config := await db.row(
            "SELECT * FROM guild_config WHERE guild_id = $1", event.guild_id, record_cls=GuildConfig
        )
    ) is None:
        logger.error("No guild config")
        return
    if guild_config.log_channel_id is None:
        logger.error("No log channel")
        return

    if event.old_message is None:
        logger.error("No old message")

    diff = difflib.Differ().compare(
        event.old_message.content.split("\n") if event.old_message and event.old_message.content else [""],
        event.message.content.split("\n") if event.message.content else [""],
    )
    await bot.rest.create_message(guild_config.log_channel_id, f"```diff\n{chr(10).join(diff)}```")
