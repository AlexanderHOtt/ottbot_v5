# -*- coding=utf-8 -*-
"""Hooks for the bot."""
from uuid import uuid4 as uuid

import hikari
import tanjun

from ottbot import logger
from ottbot.constants import Colors


def _embed(ctx: tanjun.abc.Context, message: str) -> hikari.Embed:
    embed = hikari.Embed(title=f"Command Error: `/{ctx.triggering_name}`", description=message, color=Colors.ERROR)

    return embed


# TODO: return a bool instead of None
async def on_error(ctx: tanjun.abc.Context, exc: Exception) -> None:
    """General error callback."""
    if isinstance(exc, hikari.BadRequestError):
        await ctx.respond(_embed(ctx, f"**HIKARI ERRIR** ```{exc.args[0]}```"))
        raise exc

    elif isinstance(exc, hikari.ExceptionEvent):
        logger.error(f"Hikari Error: {exc}")
        await ctx.respond(
            _embed(ctx, f"**HIKARI ERROR**```{exc.args[0] if len(exc.args) > 0  else 'No error message'}```")
        )
        raise exc

    elif isinstance(exc, Exception):
        logger.error(f"General Error: {exc}")
        await ctx.respond(_embed(ctx, f"**ERROR**```{exc.args[0] if len(exc.args) > 0 else 'No error message'}```"))

        raise exc


# TODO: return a bool instead of None
async def on_parser_error(ctx: tanjun.abc.Context, exc: tanjun.ParserError) -> None:
    """Command error callback for tanjun client."""
    if isinstance(exc, (tanjun.NotEnoughArgumentsError, tanjun.TooManyArgumentsError)):
        await ctx.respond(_embed(ctx, f"**Argument Error**```{exc.message}```"))
        raise exc

    elif isinstance(exc, tanjun.MissingDependencyError):
        await ctx.respond(_embed(ctx, f"**Dependency Error**```{exc.message}```"))
        raise exc

    elif isinstance(exc, tanjun.ConversionError):
        await ctx.respond(_embed(ctx, f"**Conversion Error**```{exc.message}```"))
        raise exc

    # TODO: Add CooldownError once it exists
    else:
        raise exc


async def on_general_error(event: hikari.ExceptionEvent):
    """General error callback for the whole bot."""
    if isinstance(event.exception, hikari.BadRequestError):
        ...


async def pre_command(ctx: tanjun.abc.Context) -> None:
    """Callback that runs before each command invocation."""
    u = None
    if ctx.command:
        ctx.command.set_metadata("uuid", u := uuid())
        calls = ctx.command.metadata.get("calls", 0)
        ctx.command.set_metadata("calls", calls + 1)
    if isinstance(ctx.command, tanjun.abc.SlashCommand) and isinstance(ctx, tanjun.abc.SlashContext):
        logger.info(
            f"Running slash command /{ctx.command.parent if ctx.command.parent else ''}\
{ctx.command.name} on component{ctx.component.name if ctx.component else ''}\n{u}"
        )
