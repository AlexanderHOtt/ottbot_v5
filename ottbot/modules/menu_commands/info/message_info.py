# -*- coding=utf-8 -*-
"""Get information about the message."""

import re

import hikari
import tanjun

from ottbot.utils.embeds import EmbedFactory
from ottbot.utils.funcs import build_loaders, format_time

component, load_component, unload_component = build_loaders()


@component.with_menu_command
@tanjun.as_message_menu("Message Info", default_to_ephemeral=True)
async def message_menu_info(
    ctx: tanjun.abc.MenuContext, message: hikari.Message, bot: hikari.GatewayBot = tanjun.inject(type=hikari.GatewayBot)
) -> None:
    """Message information."""
    N = "\n"  # python doesn't allow \ in f-string expressions
    if message.content is None:
        await ctx.respond("Error: could not retrieve message content.")
        return

    desc = f"""\
Lines: `{len(message.content.split(N))}`
Words: `{len(re.split(N+"| ", message.content))}`
Characters: `{len(m := message.content.replace(N, ''))}`
Characters not including spaces: `{len(m.replace(' ', ''))}`
Sent at: {format_time(message.created_at, "F")}
{'Edited at ' + format_time(message.edited_timestamp, "F") if message.edited_timestamp else 'Not edited'}
{message.activity}
"""
    embed = EmbedFactory.build(ctx, bot, title="Message Info", desc=desc)

    await ctx.respond(embed=embed)
