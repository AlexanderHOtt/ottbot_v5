# -*- coding=utf-8 -*-
"""Hooks for the bot."""
import traceback
from uuid import uuid4 as uuid

import hikari
import tanjun

from ottbot import logger
from ottbot.constants import Colors


def _embed(ctx: tanjun.abc.Context, exc: BaseException, message: str) -> hikari.Embed:
    embed = hikari.Embed(title=f"Command Error: `/{ctx.triggering_name}`", description=message, color=Colors.ERROR)

    embed.add_field("ERROR ID", f"`{ctx.command.metadata.get('uuid', None) if ctx.command else ''}`",).add_field(
        "EXTRA INFO",
        f"""```
GUILD_ID: {ctx.guild_id}
CHANNEL_ID: {ctx.channel_id}
USER_ID: {ctx.author.id}
COMMAND_NAME: {getattr(ctx.command, "name", "")}
TIMESTAMP: {ctx.created_at}
```""",
    ).add_field("Full Traceback", f"```py\n{(''.join(traceback.format_exception(exc)))[-1000:]}```")

    return embed


# TODO: return a bool instead of None
async def on_error(ctx: tanjun.abc.Context, exc: Exception) -> None:
    """General error callback."""
    if ctx.command is None:
        logger.critical(f"No command on err callback, exc: {exc}")
        return
    uuid = ctx.command.metadata.get("uuid", None)
    if isinstance(exc, hikari.BadRequestError):
        logger.error(f"Bad Request({uuid}): {exc}")
        await ctx.respond(_embed(ctx, exc, f"**HIKARI ERROR** ```{exc.args[0]}```"))
        raise exc

    elif isinstance(exc, hikari.ExceptionEvent):
        logger.error(f"Hikari Error({uuid}): {exc}")
        await ctx.respond(
            _embed(ctx, exc, f"**HIKARI ERROR**```{exc.args[0] if len(exc.args) > 0  else 'No error message'}```")
        )
        raise exc

    elif isinstance(exc, Exception):
        logger.error(f"General Error({uuid}): {exc}")
        await ctx.respond(
            _embed(ctx, exc, f"**ERROR**```{exc.args[0] if len(exc.args) > 0 else 'No error message'}```")
        )

        raise exc


# TODO: return a bool instead of None
async def on_parser_error(ctx: tanjun.abc.Context, exc: tanjun.ParserError) -> None:
    """Command error callback for tanjun client."""
    if isinstance(exc, (tanjun.NotEnoughArgumentsError, tanjun.TooManyArgumentsError)):
        await ctx.respond(_embed(ctx, exc, f"**Argument Error**```{exc.message}```"))
        raise exc

    elif isinstance(exc, tanjun.MissingDependencyError):
        await ctx.respond(_embed(ctx, exc, f"**Dependency Error**```{exc.message}```"))
        raise exc

    elif isinstance(exc, tanjun.ConversionError):
        await ctx.respond(_embed(ctx, exc, f"**Conversion Error**```{exc.message}```"))
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
