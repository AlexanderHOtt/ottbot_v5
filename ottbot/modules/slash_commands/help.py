# -*- coding=utf-8 -*-
"""Custom help slash command."""

import logging

import tanjun

from ottbot.utils.funcs import build_loaders

component, load_component, unload_component = build_loaders()
logger = logging.getLogger(__name__)


@component.with_slash_command
@tanjun.as_slash_command("help", "Get help with the bot.")
async def cmd_help(
    ctx: tanjun.abc.SlashContext,
    client: tanjun.Client = tanjun.inject(type=tanjun.Client),
) -> None:
    """Get help with the bot."""
    s = ""
    for cmd in client.iter_slash_commands():
        s += f"`/{cmd.name}`\n"
        logger.info(cmd.metadata)

    await ctx.respond(s)
