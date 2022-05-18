# -*- coding=utf-8 -*-
"""Hot load commands."""
import logging

import tanjun
from tanjun.errors import ModuleStateConflict

from ottbot.constants import MODULE_PATH
from ottbot.modules.load import autocomplete_path
from ottbot.utils.funcs import build_loaders, get_list_of_files, path_to_module

# import tanchi


component, load_component, unload_component = build_loaders()
logger = logging.getLogger(__name__)


@component.with_slash_command
@tanjun.with_owner_check()
@tanjun.with_str_slash_option(
    "module", "The module or command to load.", default=MODULE_PATH, autocomplete=autocomplete_path
)
@tanjun.as_slash_command("load", "Load a command or module.", default_to_ephemeral=True)
async def cmd_load(
    ctx: tanjun.abc.SlashContext, module: str, client: tanjun.Client = tanjun.inject(type=tanjun.Client)
) -> None:
    """Load a command or module."""
    if ctx.guild_id is None:
        return
    modules = get_list_of_files(module, ignore_underscores=False)

    loaded: list[str] = []
    skipped: list[str] = []
    errored: list[str] = []

    for m in modules:
        try:
            await client.load_modules_async(m)
            loaded.append(path_to_module(m))
        except ModuleStateConflict:
            skipped.append(path_to_module(m))
        except Exception as e:
            logger.error(e)
            errored.append(path_to_module(m))
    #     await ctx.respond(
    #         f"\
    # Success: {[m.stem for m in success]}\n\
    # Already Loaded: {[m.stem for m in already_loaded]}\n\
    # Error: {[str(e) for e in error]}"
    #     )
    await ctx.respond(f"L: {loaded}\nS: {skipped}\nE: {errored}")
