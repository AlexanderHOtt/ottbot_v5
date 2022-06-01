# -*- coding=utf-8 -*-
"""Message edit event listener."""

import difflib
import logging

import hikari
import tanjun
import sake

from ottbot.db import AsyncPGDatabase, GuildConfig
from ottbot.utils.funcs import build_loaders, full_name, get_member, message_link
from ottbot.utils.embeds import EmbedFactory
from ottbot.constants import ZWJ, Colors

component, load_component, unload_component = build_loaders()
logger = logging.getLogger(__name__)


@component.with_listener(hikari.GuildMessageUpdateEvent)
async def lsnr_guild_message_edit(
    event: hikari.GuildMessageUpdateEvent,
    bot: hikari.GatewayBot = tanjun.inject(type=hikari.GatewayBot),
    redis: sake.RedisCache = tanjun.inject(type=sake.RedisCache),
    db: AsyncPGDatabase = tanjun.inject(type=AsyncPGDatabase),
) -> None:
    """On member join event listener."""
    if not event.is_human:
        return
    logger.info(f"Message Edit in {event.guild_id}")

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

    # Calculate diff
    if event.old_message is None:
        logger.error("No old message")

    diff = difflib.Differ().compare(
        event.old_message.content.split("\n") if event.old_message and event.old_message.content else [""],
        event.message.content.split("\n") if event.message.content else [""],
    )
    diff_txt = "\n".join(diff).replace("```", f"``{ZWJ}`")

    # Construct message
    fields = [
        ("Before", event.old_message.content if event.old_message and event.old_message.content else "", False),
        ("After", event.message.content or "", False),
        ("Diff", f"```diff\n{diff_txt}```", False),
    ]

    if event.author_id is not hikari.UNDEFINED:
        member = await get_member(event.guild_id, event.author_id, bot.cache, redis, bot.rest)
        header_text = full_name(member)
    else:
        header_text = "None"

    title = "Message edit"
    if (ch := event.get_channel()) and ch.name:
        title += f" in #{ch.name}"

    embed = EmbedFactory.build(
        event,
        bot,
        header=header_text,
        header_icon=event.author.display_avatar_url if event.author else "None",
        title=title,
        desc=f"[Jump to message]({message_link(event.guild_id, event.channel_id, event.message_id)})",
        color=Colors.INFO,
        fields=fields,
        footer=f"ID: {event.message_id}",
    )

    # Send message
    await bot.rest.create_message(guild_config.log_channel_id, embed=embed)
