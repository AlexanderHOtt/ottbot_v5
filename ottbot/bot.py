# -*- coding=utf-8 -*-
"""Create and configure differet Discord bot types."""
import typing as t

import hikari
import tanjun
import yuyo

from ottbot import config as config_


def build_bot(config: config_.FullConfig | None = None) -> hikari.GatewayBot:
    """Builds and configures a `GatewayBot`."""
    if config is None:
        config = config_.FullConfig.from_env()

    bot = hikari.GatewayBot(
        config.tokens.bot,
        logs=config.log_level,
        intents=config.intents,
        cache_settings=hikari.impl.CacheSettings(components=config.cache),
    )

    client = build_client(bot, config)
    register_client_deps(bot, client, config)

    return bot


def build_client(bot: hikari.GatewayBot, config: config_.FullConfig | None = None) -> tanjun.Client:
    """Builds and configures a `tanjun.Client`."""
    if config is None:
        config = config.FullConfig.from_env()

    client = tanjun.Client.from_gateway_bot(bot, declare_global_commands=config.declare_global_commands)

    return client


def register_client_deps(
    bot: hikari.GatewayBot, client: tanjun.Client, config: config_.FullConfig | None = None
) -> None:
    """Register `tanjun.Client` callabacks and dependencies."""
    if config is None:
        config = config_.FullConfig.from_env()

    component_client = yuyo.ComponentClient.from_gateway_bot(bot, event_managed=False)
    reaction_client = yuyo.ReactionClient.from_gateway_bot(bot, event_managed=False)

    client.add_prefix(config.prefixes)

    (
        client.add_client_callback(tanjun.ClientCallbackNames.STARTING, component_client.open)
        .add_client_callback(tanjun.ClientCallbackNames.CLOSING, component_client.close)
        .add_client_callback(tanjun.ClientCallbackNames.STARTING, reaction_client.open)
        .add_client_callback(tanjun.ClientCallbackNames.CLOSING, reaction_client.close)
        # Dep injection
    )

    if config.owner_only:
        client.with_checks(tanjun.checks.OwnerCheck())

    return client
