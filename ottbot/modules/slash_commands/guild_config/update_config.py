# -*- coding=utf-8 -*-
"""Commands related to updating a guild's configuration.

/config list

"""

import tanjun
from ottbot.db import AsyncPGDatabase, GuildConfig
from ottbot.utils.funcs import build_loaders

component, load_component, unload_component = build_loaders()

config = tanjun.slash_command_group("config", "Bot configuration.")


@config.with_command
@tanjun.as_slash_command("list", "List the configuration of the guild.")
async def cmd_config_list(ctx: tanjun.abc.SlashContext) -> None:
    """List the configuration in the current guild."""
    await ctx.respond("Config")
