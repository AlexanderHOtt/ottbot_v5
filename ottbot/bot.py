# -*- coding=utf-8 -*-
"""Create and configure different Discord bot types."""
import typing as t

import hikari
import sake
import tanjun
import yuyo

from ottbot import config as config_
from ottbot.db import AsyncPGDatabase
from ottbot.db.records import GuildConfig
from ottbot.utils.funcs import get_list_of_files
from ottbot.utils.hooks import on_error, on_parser_error, pre_command


def build_bot(config: config_.FullConfig | None = None) -> tuple[hikari.GatewayBot, tanjun.Client]:
    """Builds and configures a `GatewayBot`."""
    if config is None:
        config = config_.FullConfig.from_env()

    bot = hikari.GatewayBot(
        config.tokens.bot,
        logs=config.log_level,
        intents=config.intents,
        cache_settings=hikari.impl.CacheSettings(components=config.cache, max_messages=300),
    )

    client = build_client(bot, config)
    register_client_deps(bot, client, config)

    return bot, client


def build_client(bot: hikari.GatewayBot, config: config_.FullConfig | None = None) -> tanjun.Client:
    """Builds and configures a `tanjun.Client`."""
    if config is None:
        config = config_.FullConfig.from_env()

    client = tanjun.Client.from_gateway_bot(bot, declare_global_commands=config.declare_global_commands)
    client.set_hooks(
        tanjun.AnyHooks().add_on_error(on_error).add_on_parser_error(on_parser_error).set_pre_execution(pre_command)
    )
    # client.set_slash_hooks()

    return client


def register_client_deps(
    bot: hikari.GatewayBot, client: tanjun.Client, config: config_.FullConfig | None = None
) -> tanjun.Client:
    """Register `tanjun.Client` callbacks and dependencies."""
    if config is None:
        config = config_.FullConfig.from_env()

    # Yuyo clients
    component_client = yuyo.ComponentClient.from_gateway_bot(bot, event_managed=False)
    reaction_client = yuyo.ReactionClient.from_gateway_bot(bot, event_managed=False)

    # Databases
    redis_cache = sake.RedisCache(address=f"redis://{config.redis_host}", app=bot, event_manager=bot.event_manager)
    database = AsyncPGDatabase(config.database)

    # Command Prefix settings
    client.add_prefix(config.prefixes)

    async def prefix_getter(
        ctx: tanjun.abc.MessageContext, db: AsyncPGDatabase = tanjun.inject(type=AsyncPGDatabase)
    ) -> t.Iterable[str]:
        """Get the prefix for a guild."""
        if ctx.guild_id is None:
            return []
        if (
            config := await db.row(
                "SELECT * FROM guild_config WHERE guild_id = $1", ctx.guild_id, record_cls=GuildConfig
            )
        ) is not None:
            return [config.prefix]
        return []

    client.set_prefix_getter(prefix_getter)

    # Client config
    (
        client.add_client_callback(tanjun.ClientCallbackNames.STARTING, component_client.open)
        .add_client_callback(tanjun.ClientCallbackNames.CLOSING, component_client.close)
        .add_client_callback(tanjun.ClientCallbackNames.STARTING, reaction_client.open)
        .add_client_callback(tanjun.ClientCallbackNames.CLOSING, reaction_client.close)
        .add_client_callback(tanjun.ClientCallbackNames.STARTING, database.connect)
        .add_client_callback(tanjun.ClientCallbackNames.CLOSING, database.close)
        .add_client_callback(tanjun.ClientCallbackNames.STARTING, redis_cache.open)
        .add_client_callback(tanjun.ClientCallbackNames.CLOSING, redis_cache.close)
        # Dep injection
        .set_type_dependency(yuyo.ComponentClient, component_client)
        .set_type_dependency(yuyo.ReactionClient, reaction_client)
        .set_type_dependency(sake.redis.RedisCache, redis_cache)
        .set_type_dependency(AsyncPGDatabase, database)
        .set_type_dependency(config_.FullConfig, config)
    )
    client.load_modules(*get_list_of_files("./ottbot/modules"))
    if config.owner_only:
        client.with_check(tanjun.checks.OwnerCheck())

    return client
