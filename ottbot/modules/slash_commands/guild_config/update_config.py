# -*- coding=utf-8 -*-
"""Commands related to updating a guild's configuration.

/config list

"""

import hikari
import tanjun
from ottbot.db import AsyncPGDatabase
from ottbot.utils.funcs import build_loaders
from ottbot.modules.slash_commands.guild_config import get_guild_config
from ottbot.utils.embeds import EmbedFactory, FieldsT

component, load_component, unload_component = build_loaders()

config = component.with_slash_command(tanjun.slash_command_group("config", "Bot configuration."))


@config.with_command
@tanjun.as_slash_command("list", "List the configuration of the guild.")
async def cmd_config_list(
    ctx: tanjun.abc.SlashContext,
    db: AsyncPGDatabase = tanjun.inject(type=AsyncPGDatabase),
    bot: hikari.GatewayBot = tanjun.inject(type=hikari.GatewayBot),
) -> None:
    """List the configuration in the current guild."""
    if ctx.guild_id is None:
        return
    config = await get_guild_config(ctx.guild_id, db)
    await ctx.respond("Config")

    fields: FieldsT = [("Prefix", f"`{config.prefix}`", True)]
    embed = EmbedFactory.build(ctx, bot, title="**Server Configuration**", fields=fields)
    await ctx.respond(embed=embed)
    # config.


@config.with_command
@tanjun.with_channel_slash_option(
    "channel", "The channel to send welcome messages in.", types=(hikari.TextableGuildChannel,)
)
@tanjun.as_slash_command("welcome-channel", "Set the channel that welcome messages get sent in.")
async def cmd_config_welcomechannel(
    ctx: tanjun.abc.SlashContext,
    channel: hikari.TextableGuildChannel,
    db: AsyncPGDatabase = tanjun.inject(type=AsyncPGDatabase),
) -> None:
    """Update the channel the bot sends welcome messages in."""
    if ctx.guild_id is None:
        return

    await db.execute("UPDATE guild_config SET welcome_channel_id = $1 WHERE guild_id = $2", channel.id, ctx.guild_id)
    await ctx.respond(f"Updated `welcome_channel_id` to {channel.id} (<#{channel.id}>)")


@config.with_command
@tanjun.with_channel_slash_option(
    "channel", "The channel to log admin messages in.", types=(hikari.TextableGuildChannel,)
)
@tanjun.as_slash_command("log-channel", "Update the admin log channel.")
async def cmd_config_log_channel(
    ctx: tanjun.abc.SlashContext,
    channel: hikari.InteractionChannel,
    db: AsyncPGDatabase = tanjun.inject(type=AsyncPGDatabase),
) -> None:
    """Update the admin log channel."""
    if ctx.guild_id is None:
        return

    await db.execute("UPDATE guild_config SET log_channel_id = $1 WHERE guild_id = $2", channel.id, ctx.guild_id)
    await ctx.respond(f"Updated `log_channel` to <#{channel.id}>")


@config.with_command
@tanjun.with_channel_slash_option(
    "channel", "The channel to send starboard messages in.", types=(hikari.TextableGuildChannel,)
)
@tanjun.as_slash_command("starboard-channel", "Update the starboard channel.")
async def cmd_config_log_channel(
    ctx: tanjun.abc.SlashContext,
    channel: hikari.InteractionChannel,
    db: AsyncPGDatabase = tanjun.inject(type=AsyncPGDatabase),
) -> None:
    """Update the starboard channel."""
    if ctx.guild_id is None:
        return

    await db.execute("UPDATE guild_config SET log_channel_id = $1 WHERE guild_id = $2", channel.id, ctx.guild_id)
    await ctx.respond(f"Updated `log_channel` to <#{channel.id}>")
