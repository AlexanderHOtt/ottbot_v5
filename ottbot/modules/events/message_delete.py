# -*- coding=utf-8 -*-
"""Message delete event listener."""

import datetime
import logging

import hikari
import sake
import tanjun

from ottbot.constants import ZWJ, Colors
from ottbot.db import AsyncPGDatabase, GuildConfig
from ottbot.utils.embeds import EmbedFactory
from ottbot.utils.funcs import build_loaders, format_time, full_name, get_member, message_link

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

    # Construct message
    title = "Message deleted"
    desc = "None"
    if (ch := event.get_channel()) is not None:
        title += f" in #{ch.name}"
        desc = f"Jump: {ch.mention}"

    if (message := event.old_message) and (author := event.old_message.author):
        header_text = full_name(author)
        header_icon = author.display_avatar_url
        fields = [
            ("Author", author.mention, True),
            ("Created At", format_time(message.created_at, "f"), True),
        ]
    else:
        header_icon = header_text = "None"
        fields = []
    fields.append(("Deleted At", format_time(deleted_at, "f"), True))

    embed = EmbedFactory.build(
        event,
        bot,
        header=header_text,
        header_icon=header_icon,
        title=title,
        desc=desc,
        color=Colors.INFO,
        fields=fields,
        footer=f"ID: {event.message_id}",
        footer_icon="https://unsplash.it/200/200",
    )

    # Send message
    # await bot.rest.create_message(
    #     guild_config.log_channel_id,
    #     embed=hikari.Embed(
    #         title="Delete", description=desc, color=Colors.INFO, timestamp=datetime.datetime.now().astimezone()
    #     )
    #     .set_author(name=header_text, icon=header_icon)
    #     .set_footer(f"ID: {event.message_id}")
    # )
    await bot.rest.create_message(guild_config.log_channel_id, embed=embed)
    # await bot.rest.create_message(guild_config.log_channel_id, "Delete")
    # import pdb; pdb.set_trace()
