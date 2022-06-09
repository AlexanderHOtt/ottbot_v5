# -*- coding=utf-8 -*-
"""Example slash commands."""

import hikari
import tanjun

from ottbot.utils.funcs import build_loaders

component, as_loader, as_unloader = build_loaders()


@component.with_slash_command
@tanjun.as_slash_command("example_slash", "An example slash command")
async def cmd_example_slash(ctx: tanjun.abc.Context):
    await ctx.respond(f"Hello {ctx.author.mention}", user_mentions=False)


@component.with_slash_command
@tanjun.with_int_slash_option("number", "A number")
@tanjun.with_int_slash_option("number2", "A second number", choices={"One": 1, "Two": 2, "Three": 3})
@tanjun.with_str_slash_option("word", "A word, default: 'foo'", default="foo")
@tanjun.as_slash_command("example_slash_arugments", "A slash command with arguments")
async def cmd_example_slash_arguments(ctx: tanjun.abc.Context, number: int, number2: int, word: str) -> None:
    await ctx.respond(f"Number: {number}\nNumber2: {number2}\nWord: {word}")


@component.with_command
@tanjun.with_argument("number", int)
@tanjun.as_message_command("example_slash_msg")
@component.with_command
@tanjun.with_int_slash_option("number", "A number")
@tanjun.as_slash_command("example_slash_msg", "An example slash and message command")
async def cmd_slash_msg(ctx: tanjun.abc.Context, number: int) -> None:
    await ctx.respond(f"You chose {number}")


@component.with_slash_command
# you can declare an ephemeral response on the decerator
@tanjun.as_slash_command("example_ephemeral", "An example ephemeral command.", default_to_ephemeral=True)
async def cmd_example_ephemeral(ctx: tanjun.abc.SlashContext) -> None:
    await ctx.respond("Ephemeral messages can only be seen by the user who called the command.")
    # or if you use lower-level functions that have an `ephemeral` kwarg or set the message flag
    # await ctx.create_initial_response(
    #     "Ephemeral messages can only be seen by the user who called the command.", flags=hikari.MessageFlag.EPHEMERAL
    # )
    # await ctx.create_followup("They are available on any message.", ephemeral=True)
