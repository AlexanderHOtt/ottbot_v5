# -*- coding=utf-8 -*-
"""Handle reaction add and remove events."""


import typing
import hikari
import sake
import tanjun

from ottbot import logger
from ottbot.constants import Colors
from ottbot.db import AsyncPGDatabase, GuildConfig, Starboard
from ottbot.utils.funcs import build_loaders, get_member, get_message, message_link

component, load_component, unload_component = build_loaders()

# https://apps.timwhitlock.info/unicode/inspect for unicode character names of '⭐🌟✨💫'
STAR_EMOJIS = ("\N{WHITE MEDIUM STAR}", "\N{GLOWING STAR}", "\N{SPARKLES}", "\N{DIZZY SYMBOL}")


def count_stars(reactions: typing.Sequence[hikari.Reaction]) -> int:
    """Count the number of star emojis in a sequence of reactions."""
    return sum([r.count for r in reactions if r.emoji.name in STAR_EMOJIS])


def _embed(event: hikari.GuildReactionAddEvent, member: hikari.Member, message: hikari.Message) -> hikari.Embed:
    link = message_link(event.guild_id, message.channel_id, message.id)
    embed = hikari.Embed(title="Jump to message", description=message.content, url=link, color=Colors.YELLOW)
    # TODO: fix when url can be a hikari.URL
    embed.set_author(
        name=f"{member.display_name} with {count_stars(message.reactions)}x \N{WHITE MEDIUM STAR}",
        icon=member.avatar_url,
    )
    return embed


@component.with_listener(hikari.GuildReactionAddEvent)
async def lsnr_guild_reaction_add_event(
    event: hikari.GuildReactionAddEvent,
    db: AsyncPGDatabase = tanjun.inject(type=AsyncPGDatabase),
    bot: hikari.GatewayBot = tanjun.inject(type=hikari.GatewayBot),
    redis: sake.RedisCache = tanjun.inject(type=sake.RedisCache),
) -> None:
    """Handle new reactions in guilds."""
    # Exit if the guild doesn't have a starboard channel configured
    # Exit if the emoji is not the :star: emoji
    # if the message exists in the database
    # edit the message in the starboard channel
    # if it doesn't exist
    # create a db entry
    # send a message in the starboard channel
    if (
        guild_config := await db.row(
            "SELECT * from guild_config WHERE guild_id = $1", event.guild_id, record_cls=GuildConfig
        )
    ) is None:
        return
    if guild_config.starboard_channel_id is None:
        return
    if event.emoji_name not in STAR_EMOJIS:
        return

    # message = await get_message(event.channel_id, event.message_id, bot.cache, redis, bot.rest)
    message = await bot.rest.fetch_message(event.channel_id, event.message_id)
    member = await get_member(event.guild_id, event.user_id, bot.cache, redis, bot.rest)
    embed = _embed(event, member, message)
    if (
        starboard := await db.row(
            "SELECT * FROM starboard WHERE original_message_id = $1", event.message_id, record_cls=Starboard
        )
    ) is None:
        sent_msg = await event.app.rest.create_message(
            guild_config.starboard_channel_id,
            # f"Starred message with {count_stars(message.reactions)}\n{link}",
            embed=embed,
        )

        await db.execute(
            "INSERT INTO starboard \
            (original_channel_id, original_message_id, sent_channel_id, sent_message_id)\
            VALUES ($1, $2, $3, $4)",
            event.channel_id,
            event.message_id,
            guild_config.starboard_channel_id,
            sent_msg.id,
        )
    else:
        await event.app.rest.edit_message(
            starboard.sent_channel_id,
            starboard.sent_message_id,
            # f"Starred message with {count_stars(message.reactions)}\n{link}",
            embed=embed,
        )


# TODO: merge these when the issue / pr gets resolved
@component.with_listener(hikari.GuildReactionDeleteEmojiEvent)
@component.with_listener(hikari.GuildReactionDeleteEvent)
async def lsnr_guild_reaction_delete_event(
    event: hikari.GuildReactionDeleteEvent | hikari.GuildReactionDeleteEmojiEvent,
    db: AsyncPGDatabase = tanjun.inject(type=AsyncPGDatabase),
    bot: hikari.GatewayBot = tanjun.inject(type=hikari.GatewayBot),
    redis: sake.RedisCache = tanjun.inject(type=sake.RedisCache),
) -> None:
    """Edit the starboard message when someone removes a star from the original message."""
    # Exit if the guild doesn't have a starboard channel configured
    # Exit if the emoji is not the :star: emoji
    # if the message exists in the database
    #   if there are no stars on the message
    #       delete the db entry and the sent message
    #   else edit the message in the starboard channel
    # if it doesn't exist
    #   create a db entry
    #   send a message in the starboard channel
    if (
        guild_config := await db.row(
            "SELECT * from guild_config WHERE guild_id = $1", event.guild_id, record_cls=GuildConfig
        )
    ) is None:
        logger.error(f"No guild config for {event.guild_id}")
        return
    if guild_config.starboard_channel_id is None:
        return
    if event.emoji_name != "star":
        return

    message = await get_message(event.channel_id, event.message_id, bot.cache, redis, bot.rest)
    link = message_link(event.guild_id, message.channel_id, message.id)
    count = len([r for r in message.reactions if r.emoji.name in STAR_EMOJIS])
    if (
        starboard := await db.row(
            "SELECT * FROM starboard WHERE original_message_id = $1", event.message_id, record_cls=Starboard
        )
    ) is None:
        if count > 0:
            sent_msg = await event.app.rest.create_message(
                guild_config.starboard_channel_id,
                f"Starred message with {count}\n{link}",
            )

            await db.execute(
                "INSERT INTO starboard \
                (original_channel_id, original_message_id, sent_channel_id, sent_message_id)\
                VALUES ($1, $2, $3, $4)",
                event.channel_id,
                event.message_id,
                guild_config.starboard_channel_id,
                sent_msg.id,
            )
    else:
        if count > 0:
            await event.app.rest.edit_message(
                starboard.sent_channel_id,
                starboard.sent_message_id,
                f"Starred message with {count_stars(message.reactions)}\n{link}",
            )
        else:
            await event.app.rest.delete_message(starboard.sent_channel_id, starboard.sent_message_id)


@component.with_listener(hikari.GuildReactionDeleteAllEvent)
async def lsnr_guild_reaction_delete_all_event(
    event: hikari.GuildReactionDeleteAllEvent,
    db: AsyncPGDatabase = tanjun.inject(type=AsyncPGDatabase),
) -> None:
    """Delete the database entry and sent message when all reactions are removed."""
    # if the guild has starboard channel, delete the sent message
    # dalete database entry
    if (
        starboard := await db.row(
            "SELECT * FROM starboard WHERE original_message_id = $1", event.message_id, record_cls=Starboard
        )
    ) is not None:
        await event.app.rest.delete_message(starboard.sent_channel_id, starboard.sent_message_id)
    await db.execute("DELETE * FROM starboard WHERE original_channel_id = $1", event.message_id)
