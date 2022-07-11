# -*- coding=utf-8 -*-
"""Handle reaction add and remove events."""


import hikari
from ottbot.db import AsyncPGDatabase, GuildConfig, Starboard
from ottbot.utils.funcs import build_loaders, get_message
import tanjun
import sake

component, load_component, unload_component = build_loaders()


@component.with_listener(hikari.GuildReactionAddEvent)
async def lsnr_guild_reaction_add_event(
    event: hikari.GuildReactionAddEvent,
    db: AsyncPGDatabase = tanjun.inject(type=AsyncPGDatabase),
    bot: hikari.GatewayBot = tanjun.inject(type=hikari.GatewayBot),
    redis: sake.RedisCache = tanjun.inject(type=sake.RedisCache),
) -> None:
    """Handle new reactions in guilds."""
    if (
        guild_config := await db.row(
            "SELECT * from guild_config WHERE guild_id = $1", event.guild_id, record_cls=GuildConfig
        )
    ) is None:
        return
    if guild_config.starboard_channel is None:
        return
    if event.emoji_name != "star":
        return

    message = await get_message(event.channel_id, event.message_id, bot.cache, redis, bot.rest)
    if (
        starboard := await db.row(
            "SELECT * FROM starboard WHERE original_message_id = $1", event.message_id, record_cls=Starboard
        )
    ) is None:
        sent_msg = await event.app.rest.create_message(
            guild_config.starboard_channel,
            f"Starred message with {len([r for r in message.reactions if r.emoji.name == 'star'])}",
        )

        await db.execute(
            "INSERT INTO starboard \
            (original_channel_id, original_message_id, sent_channel_id, sent_message_id)\
            VALUES ($1, $2, $3, $4)",
            event.channel_id,
            event.message_id,
            guild_config.starboard_channel,
            sent_msg.id,
        )
