# -*- coding=utf-8 -*-
"""Message create event listener."""

import logging

import hikari

# from ottbot.db import AsyncPGDatabase, GuildConfig
from ottbot.utils.funcs import build_loaders

# import sake
# import tanjun

component, load_component, unload_component = build_loaders()
logger = logging.getLogger(__name__)


@component.with_listener(hikari.GuildMessageCreateEvent)
async def lsnr_guild_message_create(
    event: hikari.GuildMessageCreateEvent,
    # bot: hikari.GatewayBot = tanjun.inject(type=hikari.GatewayBot),
    # redis: sake.RedisCache = tanjun.inject(type=sake.RedisCache),
    # db: AsyncPGDatabase = tanjun.inject(type=AsyncPGDatabase),
) -> None:
    """On member join event listener."""
    if not event.is_human:
        return

    # logger.info(f"Message create {event.message.content}")
