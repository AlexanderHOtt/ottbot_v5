# -*- coding=utf-8 -*-
"""Member leave or kick event listener."""

import datetime
import logging

import hikari
import sake
import tanjun
from hikari import audit_logs as hikari_audit_logs

from ottbot.constants import Colors
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


async def _build_leave_embed(
    bot: hikari.GatewayBot, event: hikari.MemberDeleteEvent, redis: sake.RedisCache, left_at: datetime.datetime
) -> hikari.Embed:
    header_text = full_name(event.user)
    header_icon = event.user.avatar_url
    desc = f"{event.user.username} left the server."
    fields: FieldsT = [("Left At", format_time(left_at, "f"), True)]
    footer = f"ID: {event.user.id}"

    try:
        member = event.old_member or await get_member(event.guild_id, event.user_id, bot.cache, redis, bot.rest)
        header_text = full_name(member)
        header_icon = member.avatar_url
        desc = f"{member.nickname} left the server."
        fields: FieldsT = [
            ("Joined At", format_time(member.joined_at, "f"), True),
            ("Left At", format_time(left_at, "f"), True),
            ("Time in Server", strfdelta(member.joined_at - left_at), True),
            ("Roles", f"{''.join([f'<&{r}>' for r in member.role_ids])}", True),
        ]
    finally:
        embed = EmbedFactory.build(
            event,
            bot,
            header=header_text,
            header_icon=header_icon,
            title="Member Leave",
            desc=desc,
            footer=footer,
            fields=fields,
            footer_icon=EMBED_ESCAPE_NAME,
            timestamp=left_at,
        )
        return embed


async def _build_kick_embed(
    bot: hikari.GatewayBot,
    event: hikari.MemberDeleteEvent,
    redis: sake.RedisCache,
    kicked_at: datetime.datetime,
    audit_log_entry: hikari_audit_logs.AuditLogEntry,
) -> hikari.Embed:
    header_text = full_name(event.user)
    header_icon = event.user.avatar_url
    desc = f"{event.user.username} was kicked from the server"
    fields: FieldsT = [("Kicked At", format_time(kicked_at, "f"), True), ("", "", True)]
    if audit_log_entry.user_id is not None:
        fields: FieldsT = [
            ("Kicked At", format_time(kicked_at, "f"), True),
            ("Kicked By", f"<@{audit_log_entry.user_id}>", True),
        ]
    footer = f"ID: {event.user.id}"

    try:
        member = event.old_member or await get_member(event.guild_id, event.user_id, bot.cache, redis, bot.rest)
        header_text = full_name(member)
        header_icon = member.avatar_url
        desc = f"{member.nickname} was kicked from the server"
        fields: FieldsT = [
            ("Joined At", format_time(member.joined_at, "f"), True),
            ("Kicked At", format_time(kicked_at, "f"), True),
            ("Time in Server", strfdelta(kicked_at - member.joined_at), True),
            ("Kicked By", f"<@{audit_log_entry.user_id}>", True),
        ]
    finally:
        embed = EmbedFactory.build(
            event,
            bot,
            header=header_text,
            header_icon=header_icon,
            color=Colors.INFO,
            title="Member Kick",
            desc=desc,
            footer=footer,
            footer_icon=EMBED_ESCAPE_NAME,
            fields=fields,
            timestamp=kicked_at,
        )
        return embed


@component.with_listener(hikari.MemberDeleteEvent)
async def lsnr_member_delete(
    event: hikari.MemberDeleteEvent,
    bot: hikari.GatewayBot = tanjun.inject(type=hikari.GatewayBot),
    redis: sake.RedisCache = tanjun.inject(type=sake.RedisCache),
    db: AsyncPGDatabase = tanjun.inject(type=AsyncPGDatabase),
) -> None:
    """On member leave or kick event listener."""
    left_or_kicked_at = datetime.datetime.now().astimezone()
    if not (
        config := await db.row("SELECT * FROM guild_config WHERE guild_id = $1", event.guild_id, record_cls=GuildConfig)
    ):
        return

    audit_log = await bot.rest.fetch_audit_log(
        event.guild_id, event_type=hikari_audit_logs.AuditLogEventType.MEMBER_KICK, user=event.user_id
    ).last()
    last_kick = sorted(audit_log.entries.values(), key=lambda x: x.created_at, reverse=True)[0]

    if last_kick.target_id == event.user_id:
        # User was kicked
        if (channel_id := config.log_channel_id) is None:
            return
        embed = await _build_kick_embed(bot, event, redis, left_or_kicked_at, last_kick)

    else:
        # User left
        if (channel_id := config.welcome_channel_id) is None:
            return
        embed = await _build_leave_embed(bot, event, redis, left_or_kicked_at)

    await bot.rest.create_message(channel_id, embed=embed)
