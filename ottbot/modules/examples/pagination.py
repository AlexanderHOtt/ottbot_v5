# -*- coding=utf-8 -*-
"""Pagination with yuyo."""
import hikrai
import tanjun
import yuyo

from ottbot.utils.funcs import build_loaders

component, load_component, unload_component = build_loaders()


@component.with_slash_command
@tanjun.as_slash_command("example_pagination", "Example pagination with yuyo.")
async def cmd_example_pagination(ctx: tanjun.abc.SlashContext) -> None:
    """Example pagination with yuyo."""
    if ctx.guild_id is None:
        return

    
