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
    await db.execute("UPDATE guild_config SET welcome_channel_id = $1", channel.id)
    await ctx.respond(f"Updated `welcome_channel_id` to {channel.id} ({channel.mention})")


@config.with_command
@tanjun.with_str_slash_option("new_prefix", "The new prefix to use for the bot.")
@tanjun.as_slash_command("prefix", "Update the guild prefix")
async def cmd_asdf(
    ctx: tanjun.abc.SlashContext,
    new_prefix: str,
    db: AsyncPGDatabase = tanjun.inject(type=AsyncPGDatabase),
) -> None:
    """Asdf."""
    if ctx.guild_id is None:
        return

    if len(new_prefix) > 5:
        await ctx.respond("The prefix is limited to 5 characters")
        return

    await db.execute("UPDATE guild_config SET prefix = $1", new_prefix)
    await ctx.respond(f"Updated `prefix` to {new_prefix}")
