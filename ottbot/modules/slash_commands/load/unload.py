# -*- coding=utf-8 -*-
"""Hot unload commands."""
import logging

import tanjun
from tanjun import ModuleStateConflict

from ottbot.constants import MODULE_PATH
from ottbot.modules.slash_commands.load import autocomplete_path
from ottbot.utils.funcs import build_loaders, get_list_of_files, path_to_module

component, load_component, unload_component = build_loaders()
logger = logging.getLogger(__name__)


@component.with_slash_command
@tanjun.with_owner_check()
@tanjun.with_str_slash_option(
    "module", "The module or command to unload.", default=MODULE_PATH, autocomplete=autocomplete_path
)
@tanjun.as_slash_command("unload", "Load a command or module.", default_to_ephemeral=True)
async def cmd_unload(
    ctx: tanjun.abc.SlashContext, module: str, client: tanjun.Client = tanjun.inject(type=tanjun.Client)
) -> None:
    """Unload a command or module."""
    if ctx.guild_id is None:
        return
    modules = get_list_of_files(
        module if module.startswith(MODULE_PATH) else MODULE_PATH + module, ignore_underscores=False
    )

    unloaded: list[str] = []
    skipped: list[str] = []
    errored: list[str] = []

    for m in modules:
        try:
            client.unload_modules(m)
            unloaded.append(path_to_module(m))
        except ModuleStateConflict:
            skipped.append(path_to_module(m))
        except Exception as e:
            logger.error(e)
            errored.append(path_to_module(m))

    await ctx.respond(f"X: {unloaded}\nS: {skipped}\nE: {errored}")
