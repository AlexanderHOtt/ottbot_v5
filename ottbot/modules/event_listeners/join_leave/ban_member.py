# -*- coding=utf-8 -*-
"""Member ban event listener."""

import datetime
import logging

import hikari
import sake
import tanjun
from hikari import audit_logs as hikari_audit_logs

from ottbot.constants import ZWJ, Colors
from ottbot.db import AsyncPGDatabase, GuildConfig
from ottbot.utils.embeds import ESCAPE_NAME as EMBED_ESCAPE_NAME
from ottbot.utils.embeds import EmbedFactory, FieldsT
from ottbot.utils.funcs import (
    build_loaders,
    format_time,
    full_name,
    get_member,
    strfdelta,
)

component, load_component, unload_component = build_loaders()
logger = logging.getLogger(__name__)


@component.with_listener(hikari.BanCreateEvent)
async def lsnr_ban_create(
    event: hikari.BanCreateEvent,
    bot: hikari.GatewayBot = tanjun.inject(type=hikari.GatewayBot),
    redis: sake.RedisCache = tanjun.inject(type=sake.RedisCache),
    db: AsyncPGDatabase = tanjun.inject(type=AsyncPGDatabase),
) -> None:
    """On member ban event listener."""
    if not (
        config := await db.row("SELECT * FROM guild_config WHERE guild_id = $1", event.guild_id, record_cls=GuildConfig)
    ):
        return
    if config.log_channel_id is None:
        return

    # Get information about event
    banned_at = datetime.datetime.now().astimezone()
    ban = await event.fetch_ban()
    ban_logs = await bot.rest.fetch_audit_log(
        event.guild_id, user=ban.user, event_type=hikari_audit_logs.AuditLogEventType.MEMBER_BAN_ADD
    )
    header_text = full_name(event.user)
    header_icon = event.user.avatar_url
    desc = f"{event.user.username} was banned by {ban.user.mention}{f' for {ban.reason}' if ban.reason else ''}"

    fields: FieldsT = [
        ("Banned At", format_time(banned_at, "f"), True),
        ("Banned By", ban.user.mention, True),
        ("# of Bans", len(ban_logs), True),
    ]
    try:
        banned_user = await get_member(event.guild_id, event.user_id, bot.cache, redis, bot.rest)
        previous_offenses = await bot.rest.fetch_audit_log(
            event.guild_id, user=banned_user, event_type=hikari_audit_logs.AuditLogEventType.MEMBER_BAN_ADD
        )

        fields: FieldsT = [
            ("Joined At", format_time(banned_user.joined_at, "f"), True),
            ("Banned At", format_time(banned_at, "f"), True),
            ("Time in Server", strfdelta(banned_at - banned_user.joined_at), True),
            ("Previous Bans", len(previous_offenses), True),
            (ZWJ, ZWJ, False),
            ("Banned By", ban.user.mention, True),
            ("# of Bans", len(ban_logs), True),
        ]

        header_text = full_name(banned_user)
        header_icon = banned_user.avatar_url
        desc = f"{banned_user.username} was banned by {ban.user.mention}{f' for {ban.reason}' if ban.reason else ''}"
    finally:
        embed = EmbedFactory.build(
            event,
            bot,
            header=header_text,
            header_icon=header_icon,
            color=Colors.INFO,
            title="User Ban",
            desc=desc,
            author=ban.user,
            footer="🔨",
            footer_icon=EMBED_ESCAPE_NAME,
            fields=fields,
        )
        await bot.rest.create_message(config.log_channel_id, embed=embed)
