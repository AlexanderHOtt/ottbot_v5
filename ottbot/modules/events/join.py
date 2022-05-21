# -*- coding=utf-8 -*-
"""On member join event listener."""

import logging

import hikari
import sake
import tanjun

from ottbot.db import AsyncPGDatabase
from ottbot.utils.funcs import build_loaders, get_text_channel

component, load_component, unload_component = build_loaders()
logger = logging.getLogger(__name__)


@component.with_listener(hikari.MemberCreateEvent)
async def lsnr_guild_member_create(
    event: hikari.MemberCreateEvent,
    bot: hikari.GatewayBot = tanjun.inject(type=hikari.GatewayBot),
    redis: sake.RedisCache = tanjun.inject(type=sake.RedisCache),
    db: AsyncPGDatabase = tanjun.inject(type=AsyncPGDatabase),
) -> None:
    """On member join event listener."""
    if (res := await db.row("SELECT channel_id, join_message FROM guild_config WHERE id = ?", event.guild_id)) is None:
        return
    (channel_id, message) = res
    if channel_id is None or message is None:
        return

    channel = await get_text_channel(int(channel_id), bot.cache, redis, bot.rest)

    await channel.send(message)
