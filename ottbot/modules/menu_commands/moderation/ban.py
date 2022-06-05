# -*- coding=utf-8 -*-
"""Ban menu command."""

import hikari
import tanjun

from ottbot.utils.funcs import build_loaders

component, load_component, unload_component = build_loaders()


@component.with_menu_command
@tanjun.as_user_menu("Ban")
async def user_menu_ban(
    ctx: tanjun.abc.AutocompleteContext,
    user: hikari.User | hikari.InteractionMember,
) -> None:
    """Ban the user."""
    if ctx.guild_id is None:
        return
    await ctx.rest.ban_user(ctx.guild_id, user)


@component.with_menu_command
@tanjun.as_message_menu("Ban User")
async def message_menu_ban(ctx: tanjun.abc.AutocompleteContext, message: hikari.Message):
    """Ban the user."""
    if ctx.guild_id is None:
        return

    await ctx.rest.ban_user(ctx.guild_id, message.author)
