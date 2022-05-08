# -*- coding=utf-8 -*-
"""Create and configure differet Discord bot types."""
import hikari


def build_bot() -> hikari.GatewayBot:
    """Builds and configures a `GatewayBot`."""
    bot = hikari.GatewayBot(
        "token",
        logs="",
        intents=hikari.Intents.ALL,
    )

    return bot
