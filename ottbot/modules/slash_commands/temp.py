# -*- coding=utf-8 -*-
"""Temporary placed slash commands that will have a new home soon."""

import datetime
import time
from platform import python_version

import distro
import hikari
import tanjun
from psutil import Process, virtual_memory

from ottbot import VERSION, logger
from ottbot.db import AsyncPGDatabase
from ottbot.utils.embeds import EmbedFactory, FieldsT
from ottbot.utils.funcs import build_loaders

component, load_component, unload_component = build_loaders(__name__)


@component.with_slash_command
@tanjun.as_slash_command("ping", "Pong!")
async def cmd_ping(
    ctx: tanjun.abc.SlashContext, bot: hikari.GatewayBot = tanjun.inject(type=hikari.GatewayBot)
) -> None:
    """Responds with 'Pong'."""
    if not ctx.command:
        logger.error("No command")
        return
    logger.info(f"inside ping {ctx.command}")

    before = time.perf_counter()
    msg = await ctx.respond(
        f"Pong! `{ctx.command.metadata.get('uuid', None)}`\nCalls: {ctx.command.metadata.get('calls', None)}",
        ensure_result=True,
    )
    after = time.perf_counter()

    await msg.edit(
        f"{msg.content}\n**GATEWAY**: {bot.heartbeat_latency * 1000:,.0f} ms\n**REST**: {(after - before) * 1000:,.0f} ms",
    )


@component.with_slash_command
@tanjun.as_slash_command("stats", "Display stats about the bot")
async def cmd_stats(
    ctx: tanjun.abc.SlashContext,
    bot: hikari.GatewayBot = tanjun.inject(type=hikari.GatewayBot),
    db: AsyncPGDatabase = tanjun.inject(type=AsyncPGDatabase),
) -> None:
    """Bot statistics."""
    proc = Process()
    with proc.oneshot():
        uptime = datetime.timedelta(seconds=time.time() - proc.create_time())
        cpu_time = str(datetime.timedelta(seconds=(cpu := proc.cpu_times()).system + cpu.user))
        mem_total = virtual_memory().total / (1024**2)
        mem_of_total = proc.memory_percent()
        mem_usage = mem_total * (mem_of_total / 100)
    guilds = bot.cache.get_guilds_view()
    
    fields: FieldsT = [
        ("hikari.GatewayBot", f"```{VERSION}```", True),
        ("Python", f"```{python_version()}```", True),
        ("Hikari", f"```{hikari.__version__}```", True),
        (
            "Users here",
            f"```{len([_ async for _ in bot.rest.fetch_members(ctx.guild_id)] if ctx.guild_id else [])}```",
            True,
        ),
        ("Total users", f"```{len(bot.cache.get_users_view()):,}```", True),
        ("Servers", f"```{len(guilds):,}```", True),
        # ("Lines of code", f"```{bot.lines.total:,}```", True),
        ("Latency", f"```{bot.heartbeat_latency * 1000:,.0f} ms```", True),
        ("Platform", f"```{distro.name()} {distro.version()}```", True),
        # (
        #     "Code breakdown",
        #     f"```| {code_p:>5.2f}% | code lines  -> {bot.lines.code:>6} |\n"
        #     + f"| {docs_p:>5.2f}% | docstrings  -> {bot.lines.docs:>6} |\n"
        #     + f"| {blank_p:>5.2f}% | blank lines -> {bot.lines.blank:>6} |\n```",
        #     False,
        # ),
        # (
        #     "Files by language",
        #     f"```| {len(bot.lines.py) / len(bot.lines) * 100:>5.2f}% | .py files   -> {len(bot.lines.py):>6} |\n"
        #     + f"| {len(bot.lines.sql) / len(bot.lines) * 100:>5.2f}% | .sql files  -> {len(bot.lines.sql):>6} |```",
        #     False,
        # ),
        (
            "Memory usage",
            f"```| {mem_of_total:>5,.2f}% | {mem_usage:,.0f} MiB  /  {(mem_total):,.0f} MiB |```",
            False,
        ),
        ("Uptime", f"```{str(uptime)[:-4]}```", True),
        ("CPU time", f"```{cpu_time[:-4]}```", True),
        (
            "Database calls since uptime",
            f"```{db.calls:,} ({db.calls / (uptime.total_seconds() / 60):,.6f}" + " / minute)```",
            False,
        ),
    ]
    await ctx.respond(
        embed=EmbedFactory.build(
            ctx,
            bot,
            header=" ",
            title="System stats",
            thumbnail=me.avatar_url if (me := bot.get_me()) is not None else "None",
            fields=fields,
            # color=me.get_me().accent_color
        ),
    )
