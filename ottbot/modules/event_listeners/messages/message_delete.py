# -*- coding=utf-8 -*-
"""Message delete event listener."""

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
from ottbot.utils.funcs import build_loaders, format_time, full_name

component, load_component, unload_component = build_loaders()
logger = logging.getLogger(__name__)


@component.with_listener(hikari.GuildMessageDeleteEvent)
async def lsnr_guild_message_delete(
    event: hikari.GuildMessageDeleteEvent,
    bot: hikari.GatewayBot = tanjun.inject(type=hikari.GatewayBot),
    redis: sake.RedisCache = tanjun.inject(type=sake.RedisCache),
    db: AsyncPGDatabase = tanjun.inject(type=AsyncPGDatabase),
) -> None:
    """On message delete event listener."""
    deleted_at = datetime.datetime.now().astimezone()
    # Get channel to send log message in
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

    # Get information about event
    title = "Message deleted"
    desc = EMBED_ESCAPE_NAME
    # append information if available
    if (ch := event.get_channel()) is not None:
        title += f" in #{ch.name}"
        desc = f"Jump: {ch.mention}"

    # try to get info about the message
    fields: FieldsT = []
    if (message := event.old_message) and (author := event.old_message.author):
        header_text = full_name(author)
        header_icon = author.display_avatar_url
        if message.content is not None:
            fields.append(("Content", message.content, False))
        fields += [
            ("Author", author.mention, True),
            ("Created At", format_time(message.created_at, "f"), True),
        ]
    else:
        header_icon = header_text = "None"
    fields.append(("Deleted At", format_time(deleted_at, "f"), True))

    # try to get who deleted the message from the audit logs
    # if there is not audit log entry, we can assume the user deleted it themselves
    audit_logs = bot.rest.fetch_audit_log(event.guild_id, event_type=hikari_audit_logs.AuditLogEventType.MESSAGE_DELETE)
    entries = (await audit_logs.last()).entries
    delete_entries = sorted(entries.values(), key=lambda x: x.created_at, reverse=True)
    if (entry := delete_entries[0]).created_at - datetime.datetime.now().astimezone() < datetime.timedelta(seconds=3):
        deleted_by = f"<@{entry.user_id}>" if entry.user_id else None
    else:
        deleted_by = event.old_message.author.mention if event.old_message and event.old_message.author else None
    if deleted_by is not None:
        fields.append(("Deleted By", deleted_by, True))

    # Construct Embed
    embed = EmbedFactory.build(
        event,
        bot,
        header=header_text,
        header_icon=header_icon,
        title=title,
        desc=desc,
        author=getattr(event.old_message, "author", None),
        color=Colors.INFO,
        fields=fields,
        footer=f"ID: {event.message_id}",
    )

    # Send message
    await bot.rest.create_message(guild_config.log_channel_id, embed=embed)
