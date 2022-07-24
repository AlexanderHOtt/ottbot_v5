# -*- coding=utf-8 -*-
"""Temporary placed slash commands that will have a new home soon."""

import tanjun

from ottbot import logger
from ottbot.utils.funcs import build_loaders

component, load_component, unload_component = build_loaders(__name__)


@component.with_slash_command
@tanjun.as_slash_command("ping", "Pong!")
async def cmd_ping(ctx: tanjun.abc.SlashContext) -> None:
    """Responds with 'Pong'."""
    if not ctx.command:
        logger.error("No command")
        return
    logger.info(f"inside ping {ctx.command.__dict__}")
    await ctx.respond(
        f"Pong! `{ctx.command.metadata.get('uuid', None)}`\nCalls: {ctx.command.metadata.get('calls', None)}"
    )

    await ctx.rest.add_role_to_member(545984256640286730, ctx.author.id, 719644994998239282)
