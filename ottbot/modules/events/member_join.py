# -*- coding=utf-8 -*-
"""Member join event listener."""

import logging

import hikari
import sake
import tanjun

from ottbot.db import AsyncPGDatabase, GuildConfig
from ottbot.utils.funcs import build_loaders

component, load_component, unload_component = build_loaders()
logger = logging.getLogger(__name__)


def _prepare_welcome_message(msg: str, event: hikari.MemberCreateEvent) -> str:
    return msg.replace("{member.display_name}", event.member.display_name).replace(  # noqa: FS003
        "{member.mention}", event.member.mention  # noqa: FS003
    )


@component.with_listener(hikari.MemberCreateEvent)
async def lsnr_guild_member_create(
    event: hikari.MemberCreateEvent,
    bot: hikari.GatewayBot = tanjun.inject(type=hikari.GatewayBot),
    redis: sake.RedisCache = tanjun.inject(type=sake.RedisCache),
    db: AsyncPGDatabase = tanjun.inject(type=AsyncPGDatabase),
) -> None:
    """On member join event listener."""
    if (
        guild_config := await db.row(
            "SELECT * FROM guild_config WHERE guild_id = $1", event.guild_id, record_cls=GuildConfig
        )
    ) is None:
        return
    if guild_config.welcome_channel_id is None or guild_config.welcome_message is None:
        return

    await bot.rest.create_message(
        guild_config.welcome_channel_id, _prepare_welcome_message(guild_config.welcome_message, event)
    )
