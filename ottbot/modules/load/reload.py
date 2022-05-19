# -*- coding=utf-8 -*-
"""Hot reload commands."""
import logging

import tanjun
from tanjun import ModuleStateConflict

from ottbot.constants import MODULE_PATH
from ottbot.modules.load import autocomplete_path
from ottbot.utils.funcs import build_loaders, get_list_of_files, path_to_module

component, load_component, unload_component = build_loaders()
logger = logging.getLogger(__name__)


@component.with_slash_command
@tanjun.with_owner_check()
@tanjun.with_str_slash_option(
    "module", "The module or command to reload.", default=MODULE_PATH, autocomplete=autocomplete_path
)
@tanjun.as_slash_command("reload", "Load a command or module.", default_to_ephemeral=True)
async def cmd_reload(
    ctx: tanjun.abc.SlashContext, module: str, client: tanjun.Client = tanjun.inject(type=tanjun.Client)
) -> None:
    """Reload a command or module."""
    if ctx.guild_id is None:
        return
    modules = get_list_of_files(
        module if module.startswith(MODULE_PATH) else MODULE_PATH + module, ignore_underscores=False
    )

    reloaded: list[str] = []
    skipped: list[str] = []
    errored: list[str] = []

    for m in modules:
        try:
            await client.reload_modules_async(m)
            reloaded.append(path_to_module(m))
        except ModuleStateConflict:
            skipped.append(path_to_module(m))
        except Exception as e:
            logger.error(e)
            errored.append(path_to_module(m))

    await ctx.respond(f"R: {reloaded}\nS: {skipped}\nE: {errored}")
