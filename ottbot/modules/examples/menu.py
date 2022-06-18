# -*- coding=utf-8 -*-
"""Example user and message apps."""
import hikari
import tanjun

from ottbot.utils.funcs import build_loaders

component, load_component, unload_component = build_loaders()


@component.with_menu_command
@tanjun.as_user_menu("Example user menu command", default_to_ephemeral=True)
async def user_menu_example(ctx: tanjun.abc.MenuContext, user: hikari.User | hikari.InteractionMember) -> None:
    """Example user menu command."""
    await ctx.respond(f"You used the example user app on {user.mention}")


@component.with_menu_command
@tanjun.as_message_menu("Example message menu command", default_to_ephemeral=True)
async def message_menu_example(ctx: tanjun.abc.MenuContext, message: hikari.Message) -> None:
    """Example message menu command."""
    await ctx.respond(f"You used the example message menu on the message with id {message.id}")
