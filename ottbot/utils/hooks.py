# -*- coding=utf-8 -*-
"""Hooks for the bot."""
import hikari
import tanjun

from ottbot.constants import Colors


def _embed(ctx: tanjun.abc.Context, message: str) -> hikari.Embed:
    embed = hikari.Embed(title=f"Command Error: /{ctx.triggering_name}", description=message, color=Colors.ERROR)

    return embed


async def on_error(ctx: tanjun.abc.Context, exc: Exception) -> None:
    """Error callback for tanjun client."""
    if isinstance(exc, hikari.BadRequestError):
        await ctx.respond(_embed(ctx, f"**HIKARI ERRIR** ```{exc.args[0]}```"))
        raise exc

    elif isinstance(exc, hikari.ExceptionEvent):
        await ctx.respond(
            _embed(ctx, f"**HIKARI ERROR**```{exc.args[0] if len(exc.args) > 0  else 'No error message'}```")
        )
        raise exc

    elif isinstance(exc, Exception):
        await ctx.respond(_embed(ctx, f"**ERROR**```{exc.args[0] if len(exc.args) > 0 else 'No error message'}```"))

        raise exc


# "CommandError",
# "ConversionError",
# "HaltExecution",
# "FailedCheck",
# "MissingDependencyError",
# "NotEnoughArgumentsError",
# "TooManyArgumentsError",
# "ParserError",
# "TanjunError",
# "TanjunWarning",
# "StateWarning",


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
